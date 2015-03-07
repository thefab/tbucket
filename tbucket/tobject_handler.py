#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.web
import tornado.gen
import json

from tbucket.redis import get_redis_pool
from tbucket.config import Config


class TObjectHandler(tornado.web.RequestHandler):

    redis_pool = None
    redis_prefix = None
    buffer_max_size = None

    def initialize(self, *args, **kwargs):
        self.redis_pool = get_redis_pool()
        self.redis_prefix = Config.redis_prefix
        self.buffer_max_size = Config.buffer_max_size

    def get_key(self, uid):
        return "%s%s" % (self.redis_prefix, uid)

    @tornado.gen.coroutine
    def get(self, uid):
        autodelete = self.get_query_argument("autodelete", default="0",
                                             strip=True)
        start = 0
        key = self.get_key(uid)
        with (yield self.redis_pool.connected_client()) as client:
            while True:
                end = start + self.buffer_max_size - 1
                chunk = yield client.call("GETRANGE", key, start, end)
                chunk_size = len(chunk)
                if chunk_size == 0:
                    if start == 0:
                        raise tornado.web.HTTPError(404)
                    else:
                        break
                if start == 0:
                    tmp = chunk.split("\r\n", 1)
                    if len(tmp) != 2:
                        raise tornado.web.HTTPError(500)
                    headers_size = int(tmp[0])
                    headers = tmp[1][0:headers_size]
                    decoded_headers = json.loads(headers)
                    for name, value in decoded_headers.items():
                        self.set_header(name, value)
                    # FIXME: minimize copy
                    chunk = tmp[1][headers_size + 2:]
                    self.set_status(200)
                self.write(chunk)
                start = start + chunk_size
                yield self.flush()
            if autodelete == "1":
                yield self._delete(uid, client)
        self.finish()

    def _delete(self, uid, client):
        key = self.get_key(uid)
        return client.call("DEL", key)

    @tornado.gen.coroutine
    def delete(self, uid):
        with (yield self.redis_pool.connected_client()) as client:
            res = yield self._delete(uid, client)
            if res != 1:
                raise tornado.web.HTTPError(404)
            self.set_status(204)
            self.finish()
