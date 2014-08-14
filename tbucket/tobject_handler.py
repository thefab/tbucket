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

    def get_object_or_raise_404(self, uid):
        tobject = self.manager.get_object_by_uid(uid)
        if tobject is None:
            raise tornado.web.HTTPError(404)
        return tobject

    @tornado.gen.coroutine
    def get(self, uid):
        tobject = self.get_object_or_raise_404(uid)
        yield tobject.seek0()
        self.set_status(200)
        for name, value in tobject.extra_headers.items():
            self.set_header(name, value)
        while True:
            tmp = yield tobject.read(Config.read_page_size)
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
        tobject = self.get_object_or_raise_404(uid)
        res = yield self.manager.remove_object_and_free_it(tobject)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def delete(self, uid):
        res = yield self._delete(uid)
        if res is None:
            raise tornado.web.HTTPError(404)
        self.set_status(204)
        self.finish()
