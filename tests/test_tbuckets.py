#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TemporaryBucketManager
from support import test_redis_or_raise_skiptest


class TBucketsTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return tbucket_get_app()

    def setUp(self, storage_method="stringio"):
        super(TBucketsTestCase, self).setUp()
        TemporaryBucketManager.make_instance(storage_method=storage_method)

    def tearDown(self):
        req = HTTPRequest(self.get_url("/tbuckets"), method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        TemporaryBucketManager.destroy_instance()
        super(TBucketsTestCase, self).tearDown()

    # compatibility with python 2.6
    def assertIn(self, str1, str2):
        self.assertTrue(str1 in str2)

    def test_post(self):
        body = "foobar"
        req = HTTPRequest(self.get_url("/tbuckets"), method="POST", body=body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith('http://'))


class TBucketsRedisTestCase(TBucketsTestCase):

    def setUp(self):
        test_redis_or_raise_skiptest()
        super(TBucketsRedisTestCase, self).setUp(storage_method="redis")
