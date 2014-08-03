#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.


def get_base_url_from_request(request):
    return "%s://%s" % (request.protocol, request.host)
