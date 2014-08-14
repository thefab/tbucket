#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.web
import tornado.gen
from tornado.web import stream_request_body
from tornado.web import HTTPError

import tbucket
from tbucket.model import TObjectManager
from tbucket.utils import get_base_url_from_request
from tbucket.config import Config


@stream_request_body
class TObjectsHandler(tornado.web.RequestHandler):

    manager = None
    write_page_size = None
    tobject = None
    parts = None
    buffer_length = None
    __buffer = None

    def initialize(self, *args, **kwargs):
        self.manager = TObjectManager.get_instance()
        self.parts = []
        self.buffer_length = 0
        self.write_page_size = Config.write_page_size

    @tornado.gen.coroutine
    def post(self):
        if self.buffer_length > 0:
            yield self._data_flush()
        yield self.tobject.flush()
        self.manager.add_object(self.tobject)
        self.set_status(201)
        base_url = get_base_url_from_request(self.request)
        tobject_path = self.reverse_url(tbucket.TOBJECT_URL_SPEC_NAME,
                                        self.tobject.uid)
        tobject_url = "%s%s" % (base_url, tobject_path)
        self.add_header('Location', tobject_url)
        self.finish()

    @tornado.gen.coroutine
    def delete(self):
        yield self.manager.purge()
        self.set_status(204)
        self.finish()

    def _get_requested_lifetime(self):
        tmp = self.request.headers.get(tbucket.LIFETIME_HEADER, None)
        if tmp is None:
            return None
        try:
            return int(tmp)
        except ValueError:
            raise tornado.web.HTTPError(status_code=400)

    def _get_requested_extra_headers(self):
        out = {}
        for key, value in self.request.headers.items():
            if key.startswith(tbucket.EXTRA_HEADER_PREFIX):
                new_key = key[len(tbucket.EXTRA_HEADER_PREFIX):]
                out[new_key] = value
        return out

    def prepare(self):
        if self.request.method == 'POST':
            self.prepare_post_request()
        elif self.request.method == 'DELETE':
            self.prepare_delete_request()
        else:
            raise HTTPError(405)

    def prepare_delete_request(self):
        pass

    def prepare_post_request(self):
        lifetime = self._get_requested_lifetime()
        extra_headers = self._get_requested_extra_headers()
        if lifetime is None:
            lifetime = Config.default_lifetime
        self.tobject = self.manager.make_object(lifetime=lifetime,
                                                extra_headers=extra_headers)

    @tornado.gen.coroutine
    def _data_flush(self):
        yield self.tobject.append(b"".join(self.parts))
        self.parts = []
        self.buffer_length = 0

    @tornado.gen.coroutine
    def data_received(self, data):
        if self.request.method == 'POST':
            data_len = len(data)
            self.parts.append(data)
            self.buffer_length = self.buffer_length + data_len
            if self.buffer_length >= self.write_page_size:
                yield self._data_flush()
