#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
import tornado.options

import tbucket.config


class ConfigTestCase(tornado.testing.AsyncTestCase):

    def tearDown(self):
        tbucket.config.Config.reset()

    def test_config1(self):
        tbucket.config.Config.port = 1234
        self.assertEqual(tbucket.config.Config.port, 1234)

    def test_config2(self):
        self.assertEqual(tbucket.config.Config.port,
                         tbucket.config.DEFAULT_DAEMON_PORT)

    def __test_config3(self):
        tbucket.config.Config.foobar

    def test_config3(self):
        self.assertRaises(AttributeError, self.__test_config3)

    def test_config4(self):
        saved = tornado.options.options
        tornado.options.options = {"port": 4567}  # we mock tornado.options
        self.assertEqual(tbucket.config.Config.port, 4567)
        tornado.options.options = saved
