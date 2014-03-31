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

LOGGING = {
    'FORMAT': u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
    'FILE': u'client.log',
}

CLIENT_SOCKET = {
    'BUFFER_SIZE': 4096,
    'HOST': 'localhost',
    'PORT': 9090,
}