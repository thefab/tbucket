#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import functools
import logging
import signal
import time

import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.httpserver import HTTPServer
from tornado.options import options as tornado_options

from tbucket.hello_handler import HelloHandler
from tbucket.tbuckets_handler import TBucketsHandler
from tbucket.tbucket_handler import TBucketHandler
from tbucket.model import TemporaryBucketManager
import tbucket


@tornado.gen.coroutine
def garbage_collection():
    '''
    @summary: function called by tornado/ioloop every n second

    It's used for garbage collection
    '''
    logging.debug("Starting garbage collection...")
    n = yield TemporaryBucketManager.get_instance().garbage_collect()
    logging.debug("%i records garbage collected", n)


def get_app():
    '''
    @summary: returns the tornado application
    @param unit_testing: if True, we add some handler for unit testing only
    @result: the tornado application
    '''
    url_list = [
        tornado.web.URLSpec(r"/", HelloHandler,
                            name=tbucket.ROOT_URL_SPEC_NAME),
        tornado.web.URLSpec(r"/tbuckets", TBucketsHandler,
                            name=tbucket.TBUCKETS_URL_SPEC_NAME),
        tornado.web.URLSpec(r"/tbuckets/(\w+)", TBucketHandler,
                            name=tbucket.TBUCKET_URL_SPEC_NAME),
    ]
    application = tornado.web.Application(url_list)
    return application


def get_ioloop(gc_interval):
    '''
    @summary: returns a configured tornado ioloop
    '''
    iol = tornado.ioloop.IOLoop.instance()
    callback = tornado.ioloop.PeriodicCallback(garbage_collection,
                                               gc_interval * 1000,
                                               iol)
    callback.start()
    return iol


def log_is_ready():
    '''
    @summary: simple callback just to log that the daemon is ready
    '''
    logging.info("tbucket daemon is ready !")


def sigterm_handler(server, loop, signum, frame):
    logging.info("SIGTERM signal catched => scheduling stop...")
    loop.add_callback(functools.partial(stop_server, server, loop))


def stop_server(server, loop):
    logging.info("Stopping tbucket...")
    server.stop()
    if loop:
        logging.info("tbucket stopped => scheduling main loop stop...")
        loop.add_timeout(time.time() + 5, functools.partial(stop_loop, loop))
    else:
        logging.info("tbucket stopped !")


def stop_loop(loop):
    logging.info("Stopping main loop...")
    loop.stop()
    logging.info("Main loop stopped !")


def main(start_ioloop=True, parse_cli=True):
    '''
    @summary: main function (starts the daemon)
    '''
    if parse_cli:
        tornado.options.parse_command_line()
    options = {
        "storage_method": tornado_options.storage_method,
        "daemon_port": tornado_options.port,
        "gc_interval": tornado_options.gc_interval,
        "default_lifetime": tornado_options.default_lifetime,
        "storage_module_name": tornado_options.storage_module_name,
        "page_size": tornado_options.page_size
    }
    TemporaryBucketManager.make_instance(**options)
    application = get_app()
    server = HTTPServer(application)
    server.listen(options['daemon_port'])
    iol = get_ioloop(options['gc_interval'])
    iol.add_callback(log_is_ready)
    signal.signal(signal.SIGTERM,
                  lambda s, f: sigterm_handler(server, iol, s, f))
    if start_ioloop:
        try:
            iol.start()
        except KeyboardInterrupt:
            stop_server(server, None)
        TemporaryBucketManager.destroy_instance()
        logging.info("tbucket daemon is stopped !")


if __name__ == '__main__':
    main()
