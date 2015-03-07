#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import tornado.testing
from tornado import gen
from tornado.ioloop import IOLoop

from tbucket.main import get_app as tbucket_get_app
from tbucket.main import main, get_ioloop
from tbucket.config import Config


class MainTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return tbucket_get_app()

    def setUp(self):
        super(MainTestCase, self).setUp()
        self.port = tornado.testing.bind_unused_port()[1]

    def get_new_ioloop(self):
        return get_ioloop()

    @tornado.testing.gen_test
    def test_main(self):
        Config.port = self.port
        main(start_ioloop=False, parse_cli=False)
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 3)
