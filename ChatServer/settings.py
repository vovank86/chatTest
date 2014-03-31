#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

#******************************
# Chat server settings
#******************************

LOGGING = {
    'FORMAT': u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
    'FILE': u'server.log',
}

DATABASES = {
    'default': {
        'ENGINE': 'sqlite://',
        'ROUTE': '/C:\\sqlitedbs\\',
        'NAME': 'chatTest.db',
        'DEBUG_MODE': False,
    },
    'unix': {
        'ENGINE': 'sqlite://',
        'ROUTE': '//Users/vovank86/chatTest/db/',
        'NAME': 'chatTest.db',
        'DEBUG_MODE': False,
    },
}

SERVER_SOCKET = {
    'BUFFER_SIZE': 4096,
    'HOST': '0.0.0.0',
    'PORT': 9090,
}