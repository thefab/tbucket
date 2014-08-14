#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

import tbucket
from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TObjectManager
from tbucket.config import Config
from support import test_redis_or_raise_skiptest, make_random_body


class TBucketTestCase(tornado.testing.AsyncHTTPTestCase):

    bucket_url = None
    body = make_random_body(10)

    def get_app(self):
        return tbucket_get_app()

    def setUp(self, storage_method="bytesio"):
        super(TBucketTestCase, self).setUp()
        Config.storage_method = storage_method
        headers = {}
        headers[tbucket.LIFETIME_HEADER] = "3600"
        headers["%sFooBar" % tbucket.EXTRA_HEADER_PREFIX] = "foobar"
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

    def test_get(self, test_empty_body=False):
        req = HTTPRequest(self.bucket_url, method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        if test_empty_body:
            self.assertEqual(b"", response.body)
        else:
            self.assertEqual(self.body, response.body)
        headers = response.headers
        self.assertTrue("FooBar" in headers)
        self.assertEquals(headers["FooBar"], "foobar")

    def test_get_autodelete1(self, test_empty_body=False):
        req = HTTPRequest(self.bucket_url + "?autodelete=1", method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        if test_empty_body:
            self.assertEqual(b"", response.body)
        else:
            self.assertEqual(self.body, response.body)
        req = HTTPRequest(self.bucket_url, method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_get_autodelete0(self, test_empty_body=False):
        req = HTTPRequest(self.bucket_url + "?autodelete=0", method="GET")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        if test_empty_body:
            self.assertEqual(b"", response.body)
        else:
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


class TBucketDummyTestCase(TBucketTestCase):

    def setUp(self):
        super(TBucketDummyTestCase, self).setUp(storage_method="dummy")

    def test_get(self):
        super(TBucketDummyTestCase, self).test_get(test_empty_body=True)

    def test_get_autodelete1(self):
        pass

    def test_get_autodelete0(self):
        pass
