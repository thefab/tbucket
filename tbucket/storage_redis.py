#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.gen
import tornadis
import six

from tbucket.storage import TObjectStorage
from tbucket.storage import TObjectStorageFactory, StorageException
from tbucket.config import Config

REDIS_TOBJECT_STORAGE_NAME = "redis"


class RedisTObjectStorage(TObjectStorage):

    __pool = None
    prefix = None
    pointer = None

    def __init__(self, uid, pool, prefix):
        TObjectStorage.__init__(self, uid)
        self.__pool = pool
        self.prefix = prefix
        self.pointer = 0

    def _get_redis_key(self):
        return "%s%s" % (self.prefix, self.uid)

    @tornado.gen.coroutine
    def append(self, strg):
        key = self._get_redis_key()
        with (yield self.__pool.connected_client()) as client:
            try:
                res = yield client.call("APPEND", key, strg)
            except Exception as e:
                raise StorageException(str(e))
            if not isinstance(res, six.integer_types):
                raise StorageException("redis append didn't return an int")

    @tornado.gen.coroutine
    def destroy(self):
        key = self._get_redis_key()
        with (yield self.__pool.connected_client()) as client:
            try:
                res = yield client.call("DEL", key)
            except Exception as e:
                raise StorageException(str(e))
            if not isinstance(res, six.integer_types):
                raise StorageException("redis append didn't return an int")

    @tornado.gen.coroutine
    def seek0(self):
        self.pointer = 0

    @tornado.gen.coroutine
    def flush(self):
        pass

    @tornado.gen.coroutine
    def read(self, size=-1):
        key = self._get_redis_key()
        maximum = -1
        if size != -1:
            maximum = self.pointer + size - 1
        with (yield self.__pool.connected_client()) as client:
            try:
                res = yield client.call("GETRANGE", key, self.pointer, maximum)
            except Exception as e:
                raise StorageException(str(e))
            if not isinstance(res, six.string_types):
                raise StorageException("redis getrange didn't return a string")
        self.pointer = self.pointer + len(res)
        raise tornado.gen.Return(res)


class RedisTObjectStorageFactory(TObjectStorageFactory):

    __pool = None
    prefix = None

    @staticmethod
    def get_name():
        return REDIS_TOBJECT_STORAGE_NAME

    def __init__(self):
        super(TObjectStorageFactory, self).__init__()
        host = Config.redis_host
        self.prefix = Config.redis_prefix
        port = Config.redis_port
        try:
            self.__pool = tornadis.ClientPool(host=host, port=port)
        except Exception as e:
            raise StorageException(str(e))

    def destroy(self):
        if self.__pool is not None:
            try:
                self.__pool.destroy()
            except Exception as e:
                raise StorageException(str(e))
            self.__pool = None

    def make_storage_object(self, uid):
        return RedisTObjectStorage(uid, self.__pool, self.prefix)
