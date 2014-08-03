#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

from tbucket.main import get_app as tbucket_get_app
from tbucket.model import TemporaryBucketManager


class TBucketTestCase(tornado.testing.AsyncHTTPTestCase):

    bucket_url = None
    body = "foobar" * 100000

    def get_app(self):
        return tbucket_get_app()

    def setUp(self, storage_method="stringio"):
        super(TBucketTestCase, self).setUp()
        TemporaryBucketManager.make_instance(storage_method=storage_method)
        req = HTTPRequest(self.get_url("/tbuckets"), method="POST",
                          body=self.body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 201)
        location = response.headers['Location']
        self.assertTrue(location.startswith('http://'))
        self.bucket_url = location

    def tearDown(self):
        req = HTTPRequest(self.get_url("/tbuckets"), method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        TemporaryBucketManager.destroy_instance()
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
        super(TBucketRedisTestCase, self).setUp(storage_method="redis")
