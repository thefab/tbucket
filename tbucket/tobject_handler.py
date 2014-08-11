#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.web
import tornado.gen

from tbucket.model import TObjectManager
from tbucket.config import Config


class TObjectHandler(tornado.web.RequestHandler):

    manager = None

    def initialize(self, *args, **kwargs):
        self.manager = TObjectManager.get_instance()

    def get_bucket_or_raise_404(self, uid):
        tbucket = self.manager.get_bucket_by_uid(uid)
        if tbucket is None:
            raise tornado.web.HTTPError(404)
        return tbucket

    @tornado.gen.coroutine
    def get(self, uid):
        tbucket = self.get_bucket_or_raise_404(uid)
        yield tbucket.seek0()
        self.set_status(200)
        for name, value in tbucket.extra_headers.items():
            self.set_header(name, value)
        while True:
            tmp = yield tbucket.read(Config.read_page_size)
            if tmp == "":
                break
            self.write(tmp)
            yield self.flush()
        autodelete = self.get_query_argument("autodelete", default="0",
                                             strip=True)
        if autodelete == "1":
            yield self._delete(uid)
        self.finish()

    @tornado.gen.coroutine
    def _delete(self, uid):
        tbucket = self.get_bucket_or_raise_404(uid)
        res = yield self.manager.remove_bucket_and_free_it(tbucket)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def delete(self, uid):
        res = yield self._delete(uid)
        if res is None:
            raise tornado.web.HTTPError(404)
        self.set_status(204)
        self.finish()
