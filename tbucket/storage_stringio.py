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
from tbucket.storage import StorageException
from tbucket.storage import TObjectStorageFactory

STRINGIO_TOBJECT_STORAGE_NAME = "stringio"


class StringIOTObjectStorage(TObjectStorage):
    """Class to store the body of a transient object in a (c)StringIO object
    """

    __sio = None

    def __init__(self, uid):
        TObjectStorage.__init__(self, uid)
        self.__sio = StringIO()

    @tornado.gen.coroutine
    def append(self, strg):
        try:
            self.__sio.write(strg)
        except Exception as e:
            raise StorageException(e.message)

    @tornado.gen.coroutine
    def destroy(self):
        if self.__sio is not None:
            try:
                self.__sio.close()
            except Exception as e:
                raise StorageException(e.message)
            self.__sio = None

    @tornado.gen.coroutine
    def seek0(self):
        try:
            self.__sio.seek(0)
        except Exception as e:
            raise StorageException(e.message)

    @tornado.gen.coroutine
    def read(self, size=-1):
        try:
            tmp = self.__sio.read(size)
        except Exception as e:
            raise StorageException(e.message)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def flush(self):
        pass


class StringIOTObjectStorageFactory(TObjectStorageFactory):

    @staticmethod
    def get_name():
        return STRINGIO_TOBJECT_STORAGE_NAME

    def destroy(self):
        pass

    def make_storage_object(self, uid):
        return StringIOTObjectStorage(uid)
