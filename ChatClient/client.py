#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket
import base64
import json


def connect(user_data):
    """

    @rtype : object
    """
    json_encoded = json.dumps(user_data)
    user_data = base64.b64encode(json_encoded)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9090))
    print sock.recv(1024)
    sock.send(user_data)
    data = sock.recv(1024)
    sock.close()

    if "fail" == data:
        return False
    else:
        return data