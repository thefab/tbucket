#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing

import tbucket


class BenchTestCase(tornado.testing.AsyncTestCase):

    def test_generate_1B_body(self):
        x = tbucket.bench_generate_1B_body()
        self.assertEqual(len(x), 1)

    def test_generate_1kB_body(self):
        x = tbucket.bench_generate_1kB_body()
        self.assertEqual(len(x), 1024)

    def test_generate_10kB_body(self):
        x = tbucket.bench_generate_10kB_body()
        self.assertEqual(len(x), 10240)

    def test_generate_100kB_body(self):
        x = tbucket.bench_generate_100kB_body()
        self.assertEqual(len(x), 102400)

    def test_generate_1MB_body(self):
        x = tbucket.bench_generate_1MB_body()
        self.assertEqual(len(x), 1048576)

    def test_generate_10MB_body(self):
        x = tbucket.bench_generate_10MB_body()
        self.assertEqual(len(x), 10485760)
