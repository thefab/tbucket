#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.gen

from tbucket.storage import TObjectStorage
from tbucket.storage import TObjectStorageFactory

DUMMY_TOBJECT_STORAGE_NAME = "dummy"


class DummyIOTObjectStorage(TObjectStorage):

    @tornado.gen.coroutine
    def append(self, strg):
        pass

    @tornado.gen.coroutine
    def destroy(self):
        pass

    @tornado.gen.coroutine
    def seek0(self):
        pass

    @tornado.gen.coroutine
    def read(self, size=-1):
        raise tornado.gen.Return("")

    @tornado.gen.coroutine
    def flush(self):
        pass


class DummyTObjectStorageFactory(TObjectStorageFactory):

    @staticmethod
    def get_name():
        return DUMMY_TOBJECT_STORAGE_NAME

    def destroy(self):
        pass

    def make_storage_object(self, uid):
        return DummyIOTObjectStorage(uid)
