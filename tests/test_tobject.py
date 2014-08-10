#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

import tbucket
from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TObjectManager
from tbucket.config import Config
from support import test_redis_or_raise_skiptest


class TBucketTestCase(tornado.testing.AsyncHTTPTestCase):

    bucket_url = None
    body = "foobar" * 100000

    def get_app(self):
        return tbucket_get_app()

    def setUp(self, storage_method="stringio"):
        super(TBucketTestCase, self).setUp()
        Config.storage_method = storage_method
        headers = {}
        headers[tbucket.TBUCKET_LIFETIME_HEADER] = "3600"
        headers["%sFooBar" % tbucket.TBUCKET_EXTRA_HEADER_PREFIX] = "foobar"
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="POST",
                          body=self.body, headers=headers)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith('http://'))
        self.bucket_url = location

    def tearDown(self):
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        TObjectManager.destroy_instance()
        super(TBucketTestCase, self).tearDown()

    def test_delete(self):
        req = HTTPRequest(self.bucket_url, method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        req = HTTPRequest(self.bucket_url, method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_get404(self):
        req = HTTPRequest(self.bucket_url + "foo", method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_get(self):
        req = HTTPRequest(self.bucket_url, method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(self.body, response.body)
        headers = response.headers
        self.assertTrue("FooBar" in headers)
        self.assertEquals(headers["FooBar"], "foobar")

    def test_get_autodelete1(self):
        req = HTTPRequest(self.bucket_url + "?autodelete=1", method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(self.body, response.body)
        req = HTTPRequest(self.bucket_url, method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_get_autodelete0(self):
        req = HTTPRequest(self.bucket_url + "?autodelete=0", method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(self.body, response.body)
        req = HTTPRequest(self.bucket_url, method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(self.body, response.body)


class TBucketRedisTestCase(TBucketTestCase):

    def setUp(self):
        test_redis_or_raise_skiptest()
        super(TBucketRedisTestCase, self).setUp(storage_method="redis")
