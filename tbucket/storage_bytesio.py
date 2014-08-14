#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

from io import BytesIO
import tornado.gen

from tbucket.storage import TObjectStorage
from tbucket.storage import StorageException
from tbucket.storage import TObjectStorageFactory

BYTESIO_TOBJECT_STORAGE_NAME = "bytesio"


class BytesIOTObjectStorage(TObjectStorage):

    __bio = None

    def __init__(self, uid):
        TObjectStorage.__init__(self, uid)
        self.__bio = BytesIO()

    @tornado.gen.coroutine
    def append(self, strg):
        try:
            self.__bio.write(strg)
        except Exception as e:
            raise StorageException(str(e))

    @tornado.gen.coroutine
    def destroy(self):
        if self.__bio is not None:
            try:
                self.__bio.close()
            except Exception as e:
                raise StorageException(str(e))
            self.__bio = None

    @tornado.gen.coroutine
    def seek0(self):
        try:
            self.__bio.seek(0)
        except Exception as e:
            raise StorageException(str(e))

    @tornado.gen.coroutine
    def read(self, size=-1):
        try:
            tmp = self.__bio.read(size)
        except Exception as e:
            raise StorageException(str(e))
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def flush(self):
        pass


class BytesIOTObjectStorageFactory(TObjectStorageFactory):

    @staticmethod
    def get_name():
        return BYTESIO_TOBJECT_STORAGE_NAME

    def destroy(self):
        pass

    def make_storage_object(self, uid):
        return BytesIOTObjectStorage(uid)
