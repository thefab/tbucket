#!/usr/bin/env python
# -*- coding: utf-8 -*-

version_info = (0, 0, '1')
__version__ = ".".join([str(x) for x in version_info])

ROOT_URL_SPEC_NAME = "hello"
TBUCKETS_URL_SPEC_NAME = "buckets"
TBUCKET_URL_SPEC_NAME = "bucket"
TBUCKET_LIFETIME_HEADER = "X-TBucket-Lifetime"
TBUCKET_CONTENT_TYPE_HEADER = "X-Tbucket-Content-Type"
