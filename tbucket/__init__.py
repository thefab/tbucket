#!/usr/bin/env python
# -*- coding: utf-8 -*-

version_info = (0, 0, '1')
__version__ = ".".join([str(x) for x in version_info])

ROOT_URL_SPEC_NAME = "hello"
TBUCKETS_URL_SPEC_NAME = "buckets"
TBUCKET_URL_SPEC_NAME = "bucket"
TBUCKET_LIFETIME_HEADER = "X-Tbucket-Lifetime"
TBUCKET_EXTRA_HEADER_PREFIX = "X-Tbucket-Header-"
