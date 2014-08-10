#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import uuid
import importlib
from datetime import datetime
from datetime import timedelta
import tornado.gen

from tbucket.storage import TObjectStorageFactory
from tbucket.config import Config


class TObject(object):

    uid = None
    lifetime = None
    extra_headers = None
    expired_datetime = None
    __storage = None

    def __init__(self, storage, lifetime, extra_headers={}):
        self.uid = uuid.uuid4().hex
        self.__storage = storage
        self.__storage.uid = self.uid
        ts = datetime.now() + timedelta(seconds=lifetime)
        self.expired_datetime = ts
        self.extra_headers = extra_headers

    def is_valid(self):
        return (datetime.now() <= self.expired_datetime)

    @tornado.gen.coroutine
    def append(self, strg):
        yield self.__storage.append(strg)

    @tornado.gen.coroutine
    def seek0(self):
        yield self.__storage.seek0()

    @tornado.gen.coroutine
    def read(self, size=-1):
        tmp = yield self.__storage.read(size)
        raise tornado.gen.Return(tmp)

    @tornado.gen.coroutine
    def destroy(self):
        yield self.__storage.destroy()

    @tornado.gen.coroutine
    def flush(self):
        yield self.__storage.flush()


class TObjectManager(object):

    __instance = None
    __tbuckets = None
    __storage_factory = None
    page_size = None

    @staticmethod
    def get_instance():
        if TObjectManager.__instance is None:
            TObjectManager.__instance = TObjectManager()
        return TObjectManager.__instance

    @staticmethod
    def destroy_instance():
        if TObjectManager.__instance is None:
            return
        TObjectManager.__instance.destroy()
        TObjectManager.__instance = None

    def __init__(self):
        self.__tbuckets = {}
        obj = self._make_storage_factory_instance(Config.storage_method)
        self.__storage_factory = obj
        self.page_size = Config.page_size

    def destroy(self):
        self._destroy_storage_factory_instance()

    def add_bucket(self, tbucket):
        self.__tbuckets[tbucket.uid] = tbucket

    def get_bucket_by_uid(self, uid):
        tbucket = self.__tbuckets.get(uid, None)
        if tbucket is not None:
            if tbucket.is_valid():
                return tbucket
        return None

    @tornado.gen.coroutine
    def remove_bucket_and_free_it(self, tbucket):
        tmp = self.__tbuckets.pop(tbucket.uid, None)
        if tmp is not None:
            if tmp is not tbucket:
                raise Exception("same uid for two different"
                                "tbucket instances ?")
            else:
                yield tmp.destroy()
        raise tornado.gen.Return(tmp is not None)

    @tornado.gen.coroutine
    def _remove_multiple_buckets_and_free_them(self, tbuckets_to_clean):
        yield [self.remove_bucket_and_free_it(x) for x in tbuckets_to_clean]

    @tornado.gen.coroutine
    def garbage_collect(self):
        tbuckets_to_clean = [x for x in self.__tbuckets.values()
                             if not x.is_valid()]
        yield self._remove_multiple_buckets_and_free_them(tbuckets_to_clean)
        raise tornado.gen.Return(len(tbuckets_to_clean))

    @tornado.gen.coroutine
    def purge(self):
        tbuckets_to_clean = [x for x in self.__tbuckets.values()]
        yield self._remove_multiple_buckets_and_free_them(tbuckets_to_clean)
        raise tornado.gen.Return(len(tbuckets_to_clean))

    def _get_storage_factory_class(self, name, module_name=None):
        try:
            if module_name is None:
                module_name = "tbucket.storage_%s" % name
            importlib.import_module(module_name)
        except ImportError:
            pass
        for cls in TObjectStorageFactory.__subclasses__():
            try:
                if cls.get_name() == name:
                    return cls
            except NotImplemented:
                pass
        raise Exception("not found storage method : %s" % name)

    def _make_storage_factory_instance(self, name):
        module_name = Config.storage_module_name
        cls = self._get_storage_factory_class(name, module_name)
        return cls.get_instance()

    def _destroy_storage_factory_instance(self):
        self.__storage_factory.destroy_instance()

    def make_bucket(self, lifetime=Config.default_lifetime,
                    extra_headers={}):
        storage_object = self.__storage_factory.make_storage_object()
        obj = TObject(storage_object, lifetime, extra_headers)
        return obj
