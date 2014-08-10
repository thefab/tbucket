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

    def init(self, **kwargs):
        host = kwargs.get('redis_host', 'localhost')
        self.prefix = kwargs.get('redis_prefix', 'tbuckets:')
        port = kwargs.get('redis_port', 6379)
        socket_path = kwargs.get('redis_unix_socket_path', None)
        password = kwargs.get('redis_password', None)
        selected_db = kwargs.get('redis_selected_db', None)
        self.__client = tornadoredis.Client(host=host, port=port,
                                            unix_socket_path=socket_path,
                                            password=password,
                                            selected_db=selected_db)
        self.__client.connect()

    def destroy(self):
        IOLoop.instance().run_sync(self.__client.disconnect)

    def make_storage_object(self):
        return RedisTObjectStorage(self.__client, self.prefix)
