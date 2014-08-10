#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornadoredis
import tornado.gen
from tornado.ioloop import IOLoop

from tbucket.storage import TObjectStorage
from tbucket.storage import TObjectStorageFactory
from tbucket.config import Config

REDIS_TOBJECT_STORAGE_NAME = "redis"


class RedisTObjectStorage(TObjectStorage):

    __client = None
    prefix = None
    pointer = None

    def __init__(self, client, prefix):
        TObjectStorage.__init__(self)
        self.__client = client
        self.prefix = prefix
        self.pointer = 0

    def _get_redis_key(self):
        return "%s%s" % (self.prefix, self.uid)

    @tornado.gen.coroutine
    def append(self, strg):
        key = self._get_redis_key()
        tmp = yield tornado.gen.Task(self.__client.append, key, strg)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def destroy(self):
        key = self._get_redis_key()
        tmp = yield tornado.gen.Task(self.__client.delete, key)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def seek0(self):
        self.pointer = 0
        raise tornado.gen.Return(True)

    @tornado.gen.coroutine
    def read(self, size=-1):
        key = self._get_redis_key()
        if size == -1:
            tmp = yield tornado.gen.Task(self.__client.getrange, key,
                                         self.pointer, -1)
        else:
            tmp = yield tornado.gen.Task(self.__client.getrange, key,
                                         self.pointer, self.pointer + size - 1)
        self.pointer = self.pointer + len(tmp)
        raise tornado.gen.Return(tmp)


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
        self.__client = tornadoredis.Client(host=host, port=port,
                                            unix_socket_path=socket_path,
                                            password=password)
        self.__client.connect()

    def destroy(self):
        if self.__client is not None:
            IOLoop.instance().run_sync(self.__client.disconnect)
        self.__client = None

    def make_storage_object(self):
        return RedisTObjectStorage(self.__client, self.prefix)
