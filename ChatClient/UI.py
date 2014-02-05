#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
import ttk
import client
import hashlib
import json

server_answer = {}
chat = {}

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
        global server_answer, chat
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
        #data = client.base64.b64decode(chat_data)
        #print data
        data = client.json.loads(chat_data)
        #print data
        self.chat = Frame(root)
        self.chat.pack()

        self.note = ttk.Notebook(self.chat)
        self.note.pack()


        for room in data['user_rooms']:
            #print room
            tab_inner = Frame(self.note)
            user_list = Listbox(tab_inner)
            chat_window = Text(tab_inner)
            chat_input = Entry(tab_inner, textvariable=msg)
            chat_send = Button(tab_inner, text="Send")
            chat_window.pack()
            chat_input.pack()
            chat_send.pack()
            chat_send.bind('<Button-1>', self.sendproc)

            for r_user in room['users']:
                self.user = data['user_name']

                user_list.pack()
                if r_user != self.user:
                    user_list.insert(END, r_user)

            self.note.add(tab_inner, text=room['room_name'])


    def sendproc(self, event):
        room = self.note.tab(self.note.select(), "text")
        message = {"operation": "send_mess", "user": self.user, "room": room, "text": msg.get()}
        message = json.dumps(message)
        client.s.send(message)
        msg.set('')

    def __get_active_room__(self):
        return self.note.select()



def loopproc():
    client.s.setblocking(False)
    global server_answer
    try:
        server_answer = client.s.recv(4096)
        print server_answer

        if isinstance(chat, ChatOpen):
            act_tab = chat.__get_active_room__()
            act_tab.config()
    except:
        root.after(1, loopproc)
        return
    #message = client.s.recv(1024)
    #self.chat_window.insert(END, message)
    root.after(1, loopproc)
    return



root = Tk()
msg = StringVar()
msg.set('')
root.wm_title("Chat")
obj = LoginForm()
root.after(1, loopproc)
root.mainloop()
