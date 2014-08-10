#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.gen


class TObjectStorage(object):

    uid = None

    def __init__(self, **kwargs):
        pass

    @tornado.gen.coroutine
    def append(self, strg):
        raise NotImplemented()

    @tornado.gen.coroutine
    def destroy(self):
        raise NotImplemented()

    @tornado.gen.coroutine
    def seek0(self):
        raise NotImplemented()

    @tornado.gen.coroutine
    def read(self, size=-1):
        raise NotImplemented()

    @staticmethod
    def get_name():
        raise NotImplemented()


class TObjectStorageFactory(object):

    __instance = None

    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            raise Exception("TObjectStorageFactory is not initialized")
        return cls.__instance

    @classmethod
    def make_instance(cls, **kwargs):
        if cls.__instance is not None:
            raise Exception("TObjectStorageFactory is already "
                            "initialized")
        obj = cls(**kwargs)
        obj.init(**kwargs)
        cls.__instance = obj
        return obj

    @classmethod
    def destroy_instance(cls):
        if cls.__instance is None:
            raise Exception("TObjectStorageFactory is already "
                            "deleted")
        cls.__instance.destroy()
        cls.__instance = None

    def init(self, **kwargs):
        raise NotImplemented()

    def destroy(self):
        raise NotImplemented()

    def make_storage_object(self):
        raise NotImplemented()
