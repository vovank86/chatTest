#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

#******************************
# Chat server settings
#******************************

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