#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import random
from six.moves import xrange


def make_random_body(size):
    body = "".join([random.choice(string.ascii_letters)
                    for i in xrange(0, size)])
    return body.encode()
