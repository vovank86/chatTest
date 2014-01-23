#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'vkanubrikov'

from Tkinter import *
import client
import hashlib


class LoginForm:
    def __init__(self):

        """

        @rtype : object
        """
        self.lf = Frame(root)
        self.lf.pack()
        self.lab1 = Label(self.lf, text="Login:", font="Arial 18")
        self.user_name = Entry(self.lf, width=20, bd=1)
        self.lab2 = Label(self.lf, text="Password:", font="Arial 18")
        self.password = Entry(self.lf, width=20, bd=1)
        self.button_ok = Button(self.lf, text="OK", width=30, height=5)
        self.button_ok.bind("<Button-1>", self.send_data)
        self.lab1.pack()
        self.user_name.pack()
        self.lab2.pack()
        self.password.pack()
        self.button_ok.pack()

    def send_data(self, event):
        user_data = {"operation": "login", "user": self.user_name.get(),
                     "password": hashlib.md5(self.password.get()).hexdigest()}
        server_answer = client.connect(user_data)
        if not server_answer:
            root.destroy()
        else:
            self.lf.pack_forget()
            chat = ChatOpen(server_answer)


class ChatOpen():
    def __init__(self, chat_data):
        """

        @rtype : object
        """
        # data = client.base64.b64decode(chat_data)
        # data = client.json.loads(data)

        self.chat = Frame(root)
        self.chat.pack()
        self.text = Text(self.chat)
        self.text.pack()

        self.text.bind("<Return>", self.text.insert(END, chat_data + '\n'))


root = Tk()
obj = LoginForm()
root.mainloop()