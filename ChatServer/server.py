#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import base64
import json
import db
from SocketServer import *

HOST = ''
PORT = 9090
address = (HOST, PORT)


class ChatServer(BaseRequestHandler):
    def setup(self):
        print self.client_address, 'connected!'
        self.request.send('hi ' + str(self.client_address) + '\n')

    def handle(self):
        while 1:
            data = self.request.recv(1024)
            user_data = base64.b64decode(data)
            user_data = json.loads(user_data)
            if "login" == user_data["operation"]:
                print user_data
                if not db.auth_user(user_data['user'], user_data['password']):
                    send_text = 'fail'
                else:
                    user = db.auth_user(user_data['user'], user_data['password'])
                    send_text = user.name
            print send_text

            self.request.send(send_text)
            return
            #if userData.strip() != 'bye':
            #    return

    def finish(self):
        print self.client_address, 'disconnected!'
        #self.request.send('bye ' + str(self.client_address) + '\n')

#server host is a tuple ('host', port)
server = ThreadingTCPServer(address, ChatServer)
server.serve_forever()