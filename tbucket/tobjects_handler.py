#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import json
import six
import tornado.web
import tornado.gen
from tornado.web import stream_request_body
from tornado.web import HTTPError
from tornadis import WriteBuffer

import tbucket
from tbucket.utils import get_base_url_from_request, make_uid
from tbucket.config import Config
from tbucket.redis import get_redis_pool, new_redis_pipeline


@stream_request_body
class TObjectsHandler(tornado.web.RequestHandler):

    buffer_max_size = None
    redis_prefix = None
    redis_pool = None
    uid = None
    key = None
    __buffer = None
    __append = False

    def initialize(self, *args, **kwargs):
        self.buffer_max_size = Config.buffer_max_size
        self.redis_prefix = Config.redis_prefix
        self.default_lifetime = Config.default_lifetime
        self.__append = False
        self.redis_pool = get_redis_pool()

    @tornado.gen.coroutine
    def post(self):
        yield self._data_flush()
        self.set_status(201)
        base_url = get_base_url_from_request(self.request)
        tobject_path = self.reverse_url(tbucket.TOBJECT_URL_SPEC_NAME,
                                        self.uid)
        tobject_url = "%s%s" % (base_url, tobject_path)
        self.add_header('Location', tobject_url)
        self.finish()

    @tornado.gen.coroutine
    def delete(self):
        pattern = "%s*" % self.redis_prefix
        index = "0"
        with (yield self.redis_pool.connected_client()) as client:
            while True:
                result = yield client.call("SCAN", index, "MATCH", pattern)
                if result is not None and len(result) != 2:
                    raise tornado.web.HTTPError(status_code=500)
                if len(result[1]) > 0:
                    pipeline = new_redis_pipeline()
                    for key in result[1]:
                        pipeline.stack_call("DEL", key)
                    yield client.call(pipeline)
                index = result[0]
                if index.decode() == "0":
                    break
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
                out[new_key] = value.strip()
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
        self.uid = make_uid()
        self.key = "%s%s" % (self.redis_prefix, self.uid)
        lifetime = self._get_requested_lifetime()
        extra_headers = self._get_requested_extra_headers()
        if lifetime is None:
            lifetime = self.default_lifetime
        serialized_headers = json.dumps(extra_headers)
        self.__buffer = WriteBuffer()
        tmp = "%i\r\n" % len(serialized_headers)
        if six.PY2:
            self.__buffer.append(tmp)
            self.__buffer.append(serialized_headers)
        else:
            self.__buffer.append(tmp.encode('utf-8'))
            self.__buffer.append(serialized_headers.encode('utf-8'))
        self.__buffer.append(b"\r\n")

    @tornado.gen.coroutine
    def _data_flush(self):
        if len(self.__buffer) > 0:
            with (yield self.redis_pool.connected_client()) as client:
                if self.__append:
                    yield client.call("APPEND", self.key, self.__buffer)
                else:
                    yield client.call("SET", self.key, self.__buffer)
                    self.__append = True
                self.__buffer.clear()

    @tornado.gen.coroutine
    def data_received(self, data):
        if self.request.method == 'POST':
            self.__buffer.append(data)
            if len(self.__buffer) > self.buffer_max_size:
                yield self._data_flush()
