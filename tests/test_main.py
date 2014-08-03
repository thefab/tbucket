#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import tornado.testing
from tornado import gen
from tornado.ioloop import IOLoop

from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TemporaryBucketManager
from tbucket.main import main, get_ioloop


class MainTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return tbucket_get_app()

    def setUp(self):
        super(MainTestCase, self).setUp()
        self.port = tornado.testing.bind_unused_port()

    def tearDown(self):
        TemporaryBucketManager.destroy_instance()
        super(MainTestCase, self).tearDown()

    def get_new_ioloop(self):
        return get_ioloop(1)

    @tornado.testing.gen_test
    def test_main(self):
        tornado.options.daemon_port = self.port
        main(start_ioloop=False, parse_cli=False)
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 3)
