#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

version_info = (0, 0, '1')
__version__ = ".".join([str(x) for x in version_info])

ROOT_URL_SPEC_NAME = "hello"
TOBJECTS_URL_SPEC_NAME = "tobjects"
TOBJECT_URL_SPEC_NAME = "tobject"
LIFETIME_HEADER = "X-Tbucket-Lifetime"
EXTRA_HEADER_PREFIX = "X-Tbucket-Header-"

DATA = "x" * 1000000
BODY_1KB = None
BODY_10KB = None
BODY_100KB = None
BODY_1MB = None
BODY_10MB = None


def bench_generate_1B_body(*args, **kwargs):
    return "x"


def bench_generate_1kB_body(*args, **kwargs):
    global BODY_1KB
    if BODY_1KB is None:
        BODY_1KB = "x" * 1024
    return BODY_1KB


def bench_generate_10kB_body(*args, **kwargs):
    global BODY_10KB
    if BODY_10KB is None:
        BODY_10KB = "x" * 10240
    return BODY_10KB


def bench_generate_100kB_body(*args, **kwargs):
    global BODY_100KB
    if BODY_100KB is None:
        BODY_100KB = "x" * 102400
    return BODY_100KB


def bench_generate_1MB_body(*args, **kwargs):
    global BODY_1MB
    if BODY_1MB is None:
        BODY_1MB = "x" * 1048576
    return BODY_1MB


def bench_generate_10MB_body(*args, **kwargs):
    global BODY_10MB
    if BODY_10MB is None:
        BODY_10MB = "x" * 10485760
    return BODY_10MB
