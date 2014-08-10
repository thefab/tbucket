#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import tornado.gen

from tbucket.storage import TObjectStorage
from tbucket.storage import TObjectStorageFactory

STRINGIO_TOBJECT_STORAGE_NAME = "stringio"


class StringIOTObjectStorage(TObjectStorage):

    __sio = None

    def __init__(self):
        TObjectStorage.__init__(self)
        self.__sio = StringIO()

    @tornado.gen.coroutine
    def append(self, strg):
        tmp = self.__sio.write(strg)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def destroy(self):
        tmp = self.__sio.close()
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def seek0(self):
        tmp = self.__sio.seek(0)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def read(self, size=-1):
        tmp = self.__sio.read(size)
        raise tornado.gen.Return(tmp)


class StringIOTObjectStorageFactory(TObjectStorageFactory):

    @staticmethod
    def get_name():
        return STRINGIO_TOBJECT_STORAGE_NAME

    def destroy(self):
        pass

    def make_storage_object(self):
        return StringIOTObjectStorage()
