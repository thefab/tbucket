#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import unittest
import string
import random
from six.moves import xrange


def test_redis_or_raise_skiptest(host="localhost", port=6379):
    s = socket.socket()
    try:
        s.connect((host, port))
    except socket.error:
        raise unittest.SkipTest("redis must be launched on %s:%i" % (host,
                                                                     port))


def make_random_body(size):
    body = "".join([random.choice(string.ascii_letters)
                    for i in xrange(0, size)])
    return body
