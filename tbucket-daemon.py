#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tbucket daemon released under the MIT license.
# See the LICENSE file for more information.

"""
This file is just a wrapper to start the daemon
"""
import os
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(__file__))
    from tbucket.main import main
    main()
