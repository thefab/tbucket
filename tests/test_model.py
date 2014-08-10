#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing

from tbucket.model import TObjectManager
from tbucket.main import get_app as tbucket_get_app


class ModelTestCase(tornado.testing.AsyncHTTPTestCase):

    manager = None

    def get_app(self):
        return tbucket_get_app()

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.manager = TObjectManager.make_instance()

    def tearDown(self):
        TObjectManager.destroy_instance()
        super(ModelTestCase, self).tearDown()

    @tornado.testing.gen_test
    def test_bucket_init(self):
        t = self.manager.make_bucket()
        self.assertTrue(len(t.uid) == 32)
        self.assertTrue(t.is_valid())
        yield t.destroy()

    def test_bucket_is_valid1(self):
        t = self.manager.make_bucket()
        self.assertTrue(t.is_valid())
        t.destroy()

    def test_bucket_is_valid2(self):
        t = self.manager.make_bucket(lifetime=-10)
        self.assertFalse(t.is_valid())
        t.destroy()

    @tornado.testing.gen_test
    def test_bucket_append(self):
        t = self.manager.make_bucket()
        yield t.append("foo")
        yield t.append("bar")
        yield t.seek0()
        output = yield t.read()
        self.assertEquals(output, "foobar")
        yield t.destroy()
