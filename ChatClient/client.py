#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket, base64, json
from Tkinter import *

def connect(userData):
    json_encoded = json.dumps(userData)
    userData = base64.b64encode(json_encoded)
    sock = socket.socket()
    sock.connect(('localhost', 9090))
    sock.send(userData)
    data = sock.recv(1024)
    sock.close()
    print data


class LoginForm:
    def __init__(self):
        self.lab1 = Label(root, text = "Login:", font = "Arial 18")
        self.uname = Entry(root, width = 20, bd = 1)
        self.lab2 = Label(root, text = "Password:", font = "Arial 18")
        self.password = Entry(root, width = 20, bd = 1)
        self.butOk = Button(root, text = "OK", width = 30, height = 5)
        self.butOk.bind("<Button-1>", self.send_data)
        self.lab1.pack()
        self.uname.pack()
        self.lab2.pack()
        self.password.pack()
        self.butOk.pack()

    def send_data(self, event):
        userData = {"operation":"login", "user": self.uname.get(), "password": self.password.get()}
        connect(userData)

root = Tk()
obj = LoginForm()
root.mainloop()


#userData = {"user":"root", "password":"test"}



