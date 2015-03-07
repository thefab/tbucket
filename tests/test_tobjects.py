#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from tornado.httpclient import HTTPRequest

import tbucket
from tbucket.main import get_app as tbucket_get_app

from support import make_random_body


class TBucketsTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return tbucket_get_app()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        req = HTTPRequest(self.get_url("/tbucket/objects"), method="DELETE")
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        super(TBucketsTestCase, self).tearDown()

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
