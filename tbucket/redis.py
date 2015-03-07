#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornadis

from tbucket.config import Config

TORNADIS_POOL = None


def get_redis_pool():
    global TORNADIS_POOL
    if TORNADIS_POOL is None:
        TORNADIS_POOL = tornadis.ClientPool(max_size=Config.redis_pool_size)
    return TORNADIS_POOL


def new_redis_pipeline():
    return tornadis.Pipeline()
