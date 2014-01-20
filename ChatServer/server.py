#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket, base64, json
import db

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)

conn, addr = sock.accept()

print 'connected:', addr

while True:
    data = conn.recv(1024)
    if not data:
        break
    userData = base64.b64decode(data)
    userData = json.loads(userData)
    if(userData["operation"] == "login"):
        if(db.authUser(userData['user'], userData['password'])== False):
            conn.send('Login or Password is incorrect!')
        else:
            user = db.authUser(userData['user'], userData['password'])
            sendText = 'Hello ' + user.name
        conn.send(sendText)

conn.close()



