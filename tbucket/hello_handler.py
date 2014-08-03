#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

import tornado.web


class HelloHandler(tornado.web.RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /
        '''
        print "%s://%s%s" % (self.request.protocol, self.request.host,
                             self.request.uri)
        self.write('Welcome on tbucket daemon !')
