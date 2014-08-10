#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

from tornado.options import define
import tornado.options


DEFAULT_DAEMON_PORT = 8888
DEFAULT_GC_INTERVAL = 20
DEFAULT_STORAGE_METHOD = "stringio"
DEFAULT_LIFETIME = 60
DEFAULT_PAGE_SIZE = 8192

define("port", default=DEFAULT_DAEMON_PORT, type=int,
       metavar="PORT",
       help="main port (of the tbucket daemon)", group="tbucket")

define("gc_interval", default=DEFAULT_GC_INTERVAL, type=int,
       metavar="GC_INTERVAL",
       help="garbage collection interval (in seconds, -1 => no gc)",
       group="tbucket")

define("storage_method", default=DEFAULT_STORAGE_METHOD, type=str,
       metavar="STORAGE_METHOD",
       help="storage method", group="tbucket")

define("storage_module_name", default=None, type=str,
       metavar="STORAGE_MODULE_NAME",
       help="storage module name "
            "(ex: storage_stringio, default => auto)",
       group="tbucket")

define("default_lifetime", default=DEFAULT_LIFETIME, type=int,
       metavar="DEFAULT_LIFETIME",
       help="default lifetime (in seconds)", group="tbucket")

define("page_size", default=DEFAULT_PAGE_SIZE, type=int,
       metavar="PAGE_SIZE",
       help="default page size (in bytes)", group="tbucket")


class ConfigMetaclass(type):

    __dict = {}

    def __getattr__(self, name):
        if name.startswith('__'):
            return
        if name in self.__dict:
            return self.__dict[name]
        if name in tornado.options.options:
            return tornado.options.options[name]
        raise Exception("unknown option: %s" % name)

    def __setattr__(self, name, value):
        self.__dict[name] = value


class Config(object):
    __metaclass__ = ConfigMetaclass
