#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket
import select
import sys
import json
from settings import CLIENT_SOCKET

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = CLIENT_SOCKET['HOST']
port = CLIENT_SOCKET['PORT']
buf = CLIENT_SOCKET['BUFFER_SIZE']


def connect(user_data):
    s.settimeout(2)

    try:
        s.connect((host, port))

    except:
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host.'

    user_data = json.dumps(user_data)
    s.send(user_data)

    while 1:
        socket_list = [s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(buf)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    if "fail" == data:
                        return False
                    else:
                        return data
            #user entered a message
            else:
                print 'wait'