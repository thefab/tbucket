#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

import tbucket
from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TObjectManager
from tbucket.config import Config

from support import test_redis_or_raise_skiptest, make_random_body


class TBucketsTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return tbucket_get_app()

    def setUp(self, storage_method="bytesio"):
        super(TBucketsTestCase, self).setUp()
        Config.storage_method = storage_method

    def tearDown(self):
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        TObjectManager.destroy_instance()
        super(TBucketsTestCase, self).tearDown()

    # compatibility with python 2.6
    def assertIn(self, str1, str2):
        self.assertTrue(str1 in str2)

    def test_post(self):
        body = make_random_body(1000000)
        headers = {}
        headers[tbucket.LIFETIME_HEADER] = "3600"
        headers["%sFooBar" % tbucket.EXTRA_HEADER_PREFIX] = "foobar"
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="POST",
                          body=body, headers=headers)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith('http://'))

    def test_post_uid_prefix(self):
        Config.uid_prefix = "foobar_"
        body = make_random_body(10)
        headers = {}
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="POST",
                          body=body, headers=headers)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith('http://'))
        self.assertTrue("foobar_" in location)


class TBucketsRedisTestCase(TBucketsTestCase):

    def setUp(self):
        test_redis_or_raise_skiptest()
        super(TBucketsRedisTestCase, self).setUp(storage_method="redis")


class TBucketsDummyTestCase(TBucketsTestCase):

    def setUp(self):
        super(TBucketsDummyTestCase, self).setUp(storage_method="dummy")
