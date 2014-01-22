#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

import socket
import base64
import json
from Tkinter import *

def connect(user_data):
    json_encoded = json.dumps(user_data)
    user_data = base64.b64encode(json_encoded)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9090))
    print sock.recv(1024)
    sock.send(user_data)
    print sock.recv(1024)
    sock.close()
    #print data
    #if "fail" == data:
    #    return False
    #else:
    #    return data


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
        if(connect(userData)== False):
            root.destroy()

root = Tk()
obj = LoginForm()
root.mainloop()


#userData = {"user":"root", "password":"test"}



