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
from tbucket.model import TemporaryBucketManager
from tbucket.utils import get_base_url_from_request


@stream_request_body
class TBucketsHandler(tornado.web.RequestHandler):
    """Class which handles the /tbuckets URL"""

    manager = None
    bucket = None

    def initialize(self, *args, **kwargs):
        self.manager = TemporaryBucketManager.get_instance()

    @tornado.gen.coroutine
    def post(self):
        yield self.bucket.seek0()
        self.manager.add_bucket(self.bucket)
        self.set_status(201)
        base_url = get_base_url_from_request(self.request)
        bucket_path = self.reverse_url(tbucket.TBUCKET_URL_SPEC_NAME,
                                       self.bucket.uid)
        bucket_url = "%s%s" % (base_url, bucket_path)
        self.add_header('Location', bucket_url)
        self.finish()

    @tornado.gen.coroutine
    def delete(self):
        yield self.manager.purge()
        self.set_status(204)
        self.finish()

    def _get_requested_lifetime(self):
        tmp = self.request.headers.get(tbucket.TBUCKET_LIFETIME_HEADER, None)
        if tmp is None:
            return None
        try:
            return int(tmp)
        except ValueError:
            raise tornado.web.HTTPError(status_code=400)

    def _get_requested_content_type(self):
        tmp = self.request.headers.get(tbucket.TBUCKET_CONTENT_TYPE_HEADER)
        if tmp is None:
            return None
        return tmp.strip()

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
        content_type = self._get_requested_content_type()
        if lifetime is None:
            self.bucket = self.manager.make_bucket(content_type=content_type)
        else:
            self.bucket = self.manager.make_bucket(lifetime=lifetime,
                                                   content_type=content_type)

    @tornado.gen.coroutine
    def data_received(self, data):
        if self.request.method == 'POST':
            yield self.bucket.append(data)
