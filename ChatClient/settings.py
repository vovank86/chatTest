#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

#******************************
# Chat client settings
#******************************

import sys

if sys.platform == 'darwin':
    FONT_MULTIPLIER = 1.2
else:
    FONT_MULTIPLIER = 1


CLIENT_SOCKET = {
    'BUFFER_SIZE': 4096,
    'HOST': 'localhost',
    'PORT': 9090,
}