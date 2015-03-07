#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import six


def make_random_body(size):
    return six.b("".join(["%i" % random.randint(0, 9)
                          for x in range(0, size)]))
