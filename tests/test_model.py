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
        self.manager = TObjectManager.get_instance()

    def tearDown(self):
        TObjectManager.destroy_instance()
        super(ModelTestCase, self).tearDown()

    @tornado.testing.gen_test
    def test_bucket_init(self):
        t = self.manager.make_object()
        self.assertTrue(len(t.uid) == 32)
        self.assertTrue(t.is_valid())
        yield t.destroy()

    def test_bucket_is_valid1(self):
        t = self.manager.make_object()
        self.assertTrue(t.is_valid())
        t.destroy()

    def test_bucket_is_valid2(self):
        t = self.manager.make_object(lifetime=-10)
        self.assertFalse(t.is_valid())
        t.destroy()

    @tornado.testing.gen_test
    def test_bucket_append(self):
        t = self.manager.make_object()
        yield t.append(b"foo")
        yield t.append(b"bar")
        yield t.seek0()
        output = yield t.read()
        self.assertEquals(output, b"foobar")
        yield t.destroy()
