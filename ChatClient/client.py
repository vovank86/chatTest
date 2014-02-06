#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

#import socket
#import base64
#import json


# telnet program example
import socket, select, string, sys, json


#def prompt():
#   sys.stdout.write('<You> ')
#   sys.stdout.flush()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect(user_data):
    host = 'localhost'
    port = 9090


    s.settimeout(2)

    try:
        s.connect((host, port))

    except:
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host. Start sending messages'

    user_data = json.dumps(user_data)
    s.send(user_data)

    while 1:
        socket_list = [s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
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


