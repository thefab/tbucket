#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornadoredis
import tornado.gen
from tornado.ioloop import IOLoop

from tbucket.storage import TObjectStorage
from tbucket.storage import TObjectStorageFactory, StorageException
from tbucket.config import Config

REDIS_TOBJECT_STORAGE_NAME = "redis"


class RedisTObjectStorage(TObjectStorage):

    __client = None
    prefix = None
    pointer = None

    def __init__(self, uid, client, prefix):
        TObjectStorage.__init__(self, uid)
        self.__client = client
        self.prefix = prefix
        self.pointer = 0

    def _get_redis_key(self):
        return "%s%s" % (self.prefix, self.uid)

    @tornado.gen.coroutine
    def append(self, strg):
        key = self._get_redis_key()
        try:
            res = yield tornado.gen.Task(self.__client.append, key, strg)
        except Exception as e:
            raise StorageException(e.message)
        if not isinstance(res, (int, long)):
            raise StorageException("redis append didn't return an int")

    @tornado.gen.coroutine
    def destroy(self):
        key = self._get_redis_key()
        try:
            res = yield tornado.gen.Task(self.__client.delete, key)
        except Exception as e:
            raise StorageException(e.message)
        if not isinstance(res, (int, long)):
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
        try:
            res = yield tornado.gen.Task(self.__client.getrange, key,
                                         self.pointer, maximum)
        except Exception as e:
            raise StorageException(e.message)
        if not isinstance(res, basestring):
            raise StorageException("redis getrange didn't return a string")
        self.pointer = self.pointer + len(res)
        raise tornado.gen.Return(res)


class RedisTObjectStorageFactory(TObjectStorageFactory):

    __client = None
    prefix = None

    @staticmethod
    def get_name():
        return REDIS_TOBJECT_STORAGE_NAME

    def __init__(self):
        super(TObjectStorageFactory, self).__init__()
        host = Config.redis_host
        self.prefix = Config.redis_prefix
        port = Config.redis_port
        socket_path = Config.redis_unix_socket_path
        password = Config.redis_password
        try:
            self.__client = tornadoredis.Client(host=host, port=port,
                                                unix_socket_path=socket_path,
                                                password=password)
            self.__client.connect()
        except Exception as e:
            raise StorageException(e.message)

    def destroy(self):
        if self.__client is not None:
            try:
                IOLoop.instance().run_sync(self.__client.disconnect)
            except Exception as e:
                raise StorageException(e.message)
            self.__client = None

    def make_storage_object(self, uid):
        return RedisTObjectStorage(uid, self.__client, self.prefix)
