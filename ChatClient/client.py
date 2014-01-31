#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

#import socket
#import base64
#import json


# telnet program example
import socket, select, string, sys


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()

#main function
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print 'Usage : python telnet.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host. Start sending messages'
    prompt()

    while 1:
        socket_list = [sys.stdin, s]

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
                    #print data
                    sys.stdout.write(data)
                    prompt()

            #user entered a message
            else:
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()





                #def connect(user_data):
                #    """
                #
                #    @rtype : object
                #    """
                #    json_encoded = json.dumps(user_data)
                #    user_data = base64.b64encode(json_encoded)
                #    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #    sock.connect(('localhost', 9090))
                #    print sock.recv(1024)
                #    sock.send(user_data)
                #    data = sock.recv(1024)
                #    sock.close()
                #
                #    if "fail" == data:
                #        return False
                #    else:
                #        return data