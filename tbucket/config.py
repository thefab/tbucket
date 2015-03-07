#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

from tornado.options import define
from six import add_metaclass
import tornado.options


DEFAULT_DAEMON_PORT = 8888
DEFAULT_LIFETIME = 60
DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_PASSWORD = None
DEFAULT_REDIS_PREFIX = "tbucket:"
DEFAULT_REDIS_POOL_SIZE = 500
DEFAULT_BUFFER_MAX_SIZE = 65536

define("port", default=DEFAULT_DAEMON_PORT, type=int,
       metavar="PORT",
       help="main port (of the tbucket daemon)", group="tbucket")

define("default_lifetime", default=DEFAULT_LIFETIME, type=int,
       metavar="DEFAULT_LIFETIME",
       help="default lifetime (in seconds)", group="tbucket")

define("buffer_max_size", default=DEFAULT_BUFFER_MAX_SIZE,
       type=int, metavar="BUFFER_MAX_SIZE",
       help="buffer max size", group="tbucket")

define("redis_host", default=DEFAULT_REDIS_HOST, type=str,
       metavar="REDIS_HOST",
       help="redis host", group="tbucket")

define("redis_port", default=DEFAULT_REDIS_PORT, type=int,
       metavar="REDIS_PORT",
       help="redis port", group="tbucket")

define("redis_password", default=DEFAULT_REDIS_PASSWORD, type=str,
       metavar="REDIS_PASSWORD",
       help="redis password", group="tbucket")

define("redis_prefix", default=DEFAULT_REDIS_PREFIX,
       type=str, metavar="REDIS_PREFIX",
       help="redis prefix", group="tbucket")

define("redis_pool_size", default=DEFAULT_REDIS_POOL_SIZE,
       type=int, metavar="REDIS_POOL_SIZE",
       help="redis pool size", group="tbucket")


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


@add_metaclass(ConfigMetaclass)
class Config(object):

    pass
