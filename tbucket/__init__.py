#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.options import define

version_info = (0, 0, '1')
__version__ = ".".join([str(x) for x in version_info])

DEFAULT_DAEMON_PORT = 8888
DEFAULT_GC_INTERVAL = 20
DEFAULT_STORAGE_METHOD = "stringio"
DEFAULT_LIFETIME = 60
DEFAULT_PAGE_SIZE = 8192

ROOT_URL_SPEC_NAME = "hello"
TBUCKETS_URL_SPEC_NAME = "buckets"
TBUCKET_URL_SPEC_NAME = "bucket"

TBUCKET_LIFETIME_HEADER = "X-TBucket-Lifetime"
TBUCKET_CONTENT_TYPE_HEADER = "X-Tbucket-Content-Type"

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
