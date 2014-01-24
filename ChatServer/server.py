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


def cheek_first_run():
    """
    Cheek is it a first run of the chat server or not.
    If it's the first run this function run the installation process.
    """
    session = db.Session()
    if 0 == session.query(db.User).order_by(db.User.id).count():
        db.install_chat(session)

    else:
        print '\n Now the server is starting...'


cheek_first_run()


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
                if not db.auth_user(user_data['user'], user_data['password']):
                    send_text = 'fail'
                else:
                    base_data = db.auth_user(user_data['user'], user_data['password'])
                    send_text = json.dumps(base_data)
                    send_text = base64.b64encode(send_text)

            self.request.send(send_text)
            return


    def finish(self):
        print self.client_address, 'disconnected!'

#server host is a tuple ('host', port)
server = ThreadingTCPServer(address, ChatServer)
server.serve_forever()