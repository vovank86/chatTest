#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket
import select
import sys
import json
from settings import CLIENT_SOCKET, LOGGING
import logging

logging.basicConfig(format=LOGGING['FORMAT'], level=logging.DEBUG, filename=LOGGING['FILE'])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = CLIENT_SOCKET['HOST']
port = CLIENT_SOCKET['PORT']
buf = CLIENT_SOCKET['BUFFER_SIZE']


def connect(user_data):
    s.settimeout(2)
    try:
        s.connect((host, port))
    except:
        logging.error(u'Unable to connect')
        sys.exit()

    logging.info(u'Connected to remote host.')
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
                    logging.info(u'Disconnected from chat server, no data in server answer.')
                    sys.exit()
                else:
                    if "fail" == data:
                        return False
                    else:
                        return data
            else:
                logging.info(u'wait for next server answer')