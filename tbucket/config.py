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
DEFAULT_READ_PAGE_SIZE = 131072
DEFAULT_WRITE_PAGE_SIZE = 1310720
DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_PASSWORD = None
DEFAULT_REDIS_UNIX_SOCKET_PATH = None
DEFAULT_REDIS_PREFIX = "tbucket:"

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

define("read_page_size", default=DEFAULT_READ_PAGE_SIZE, type=int,
       metavar="READ_PAGE_SIZE",
       help="default read page size (in bytes)", group="tbucket")

define("write_page_size", default=DEFAULT_WRITE_PAGE_SIZE, type=int,
       metavar="WRITE_PAGE_SIZE",
       help="default write page size (in bytes)", group="tbucket")

define("redis_host", default=DEFAULT_REDIS_HOST, type=str,
       metavar="REDIS_HOST",
       help="redis host", group="tbucket_redis")

define("redis_port", default=DEFAULT_REDIS_PORT, type=int,
       metavar="REDIS_PORT",
       help="redis port", group="tbucket_redis")

define("redis_password", default=DEFAULT_REDIS_PASSWORD, type=str,
       metavar="REDIS_PASSWORD",
       help="redis port", group="tbucket_redis")

define("redis_unix_socket_path", default=DEFAULT_REDIS_UNIX_SOCKET_PATH,
       type=str, metavar="REDIS_UNIX_SOCKET_PATH",
       help="redis socket path", group="tbucket_redis")

define("redis_prefix", default=DEFAULT_REDIS_PREFIX,
       type=str, metavar="REDIS_PREFIX",
       help="redis socket path", group="tbucket_redis")


class ConfigMetaclass(type):

    overrided_options = {}

    def __getattr__(self, name):
        if name.startswith('__'):
            # because problems with nosetests ?
            return
        if name in self.overrided_options:
            return self.overrided_options[name]
        if name in tornado.options.options:
            return tornado.options.options[name]
        raise AttributeError("unknown option: %s" % name)

    def __setattr__(self, name, value):
        self.overrided_options[name] = value

    def reset(self):
        try:
            while True:
                self.overrided_options.popitem()
        except KeyError:
            pass


class Config(object):

    __metaclass__ = ConfigMetaclass
