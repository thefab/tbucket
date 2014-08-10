#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.gen


class TObjectStorage(object):

    uid = None

    def __init__(self):
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

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def destroy_instance(cls):
        if cls.__instance is None:
            return
        cls.__instance.destroy()
        cls.__instance = None

    def destroy(self):
        raise NotImplemented()

    def make_storage_object(self):
        raise NotImplemented()
