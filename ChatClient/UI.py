#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
from CustomComponents import UserList
import ttk
import client
import hashlib
import json

#TODO: configure the Chat view using CustomComponents and grid

class LoginForm:
    def __init__(self):

        """
        Class constructor which using for creating Login Screen.
        @rtype : object
        """

        self.lf = Frame(root, padx=5, pady=5)
        self.lf.pack()
        self.title = Label(self.lf, text="myChat", font="Verdana 20")
        self.lab1 = Label(self.lf, text="Login:", font="Arial 10")
        self.user_name = Entry(self.lf, width=20, bd=1)
        self.lab2 = Label(self.lf, text="Password:", font="Arial 10")
        self.password = Entry(self.lf, width=20, bd=1, show="*")
        self.button_ok = Button(self.lf, text="Enter")
        self.button_cancel = Button(self.lf, text="Exit")
        self.button_ok.bind("<Button-1>", self.send_data)
        self.button_cancel.bind("<Button-1>", self.exit)

        self.title.grid(row=0, columnspan=4, pady=(0, 10))
        self.lab1.grid(row=1, sticky=W)
        self.lab2.grid(row=2, sticky=W)

        self.user_name.grid(row=1, column=1, columnspan=3)
        self.password.grid(row=2, column=1, columnspan=3)
        self.button_ok.grid(row=4, columnspan=2, sticky=W + E + N + S, padx=(0, 2), pady=(30, 0))
        self.button_cancel.grid(row=4, columnspan=2, column=2, sticky=W + E + N + S, padx=(2, 0), pady=(30, 0))

    def send_data(self, event):
        global server_answer, chat, chance
        user_data = {"operation": "login", "user": self.user_name.get(),
                     "password": hashlib.md5(self.password.get()).hexdigest()}
        server_answer = client.connect(user_data)
        if not server_answer:
            root.destroy()
        else:
            self.lf.pack_forget()
            chat = ChatOpen(server_answer)

    def exit(self, event):
        client.s.close()
        root.destroy()


class ChatOpen():
    def __init__(self, chat_data):
        """
        Class constructor which using for creating user interface of chat system and display Chat Screen.
        @rtype : object
        """

        data = client.json.loads(chat_data)
        self.chat = Frame(root)
        self.chat.pack()
        self.note = ttk.Notebook(self.chat)
        self.note.pack()
        self.user = data['user_name']
        self.chat_rooms = {}

        root.wm_title("myChat (" + self.user + ")")

        for room in data['user_rooms']:
            #print room
            tab_inner = Frame(self.note)
            tab_inner.configure(bg='#ffffff')
            chat_window = Text(tab_inner, font="Arial 10", foreground='#666666', width=100)
            chat_window.tag_configure("user", foreground='#3399ff')
            chat_input = Entry(tab_inner, textvariable=msg, font="Arial 10", width=80)
            chat_send = Button(tab_inner, text="Send", relief=GROOVE, bd=1, bg="#19b3e5",
                               foreground='#ffffff', activebackground='#6cfcb3')
            chat_window.grid(row=0, column=1, columnspan=2)
            chat_input.grid(row=1, column=1, sticky=W + E + N + S)
            chat_send.grid(row=1, column=2, sticky=W + E + N + S)
            chat_send.bind('<Button-1>', self.send_process)
            temp_list = room['users']
            temp_list.pop(self.user)
            user_list = UserList(tab_inner, str(room['room_name']), room['perm'], temp_list, self.user)
            user_list.grid(row=0, column=0, rowspan=2, sticky=W + N)

            #    user_list.pack()
            #    if r_user != self.user:
            #        user_list.insert(END, r_user)
            self.chat_rooms.update(
                {room['room_name']: {'instance': tab_inner, 'perm': room['perm'], 'text': chat_window,
                                     'user_list': user_list}})

            self.note.add(tab_inner, text=room['room_name'])

    def send_process(self, event):
        """ Function which using for form message package and sent it to the chat server."""
        room = self.note.tab(self.note.select(), "text")
        message = {"operation": "send_mess", "user": self.user, "room": room, "text": msg.get()}
        message = json.dumps(message)
        client.s.send(message)
        msg.set('')

    def exit(self):
        print 'exit'
        message = {"operation": "exit", "user": self.user}
        message = json.dumps(message)
        client.s.send(message)
        root.destroy()

    def get_active_room(self):
        """
        Function which using for get active room.
        @return room
        """
        room = self.note.tab(self.note.select(), "text")
        room = self.chat_rooms[room]
        return room

    def get_room(self, room_name):
        room = self.chat_rooms[room_name]
        return room

    def change_user_state(self, users_info):
        #print users_info
        for room in self.chat_rooms:
            room = self.chat_rooms.get(room)

            room_users = room.get('user_list')
            #print room_users
            room_users.change_user_state(users_info)

    def kick_user(self, user, room_name):
        room = self.get_room(room_name)
        room_users = room.get('user_list')
        #print room_users
        room_users.kick_user(user)


def loop_process():
    """ Function which using for get messages and display the message in the chat window."""
    client.s.setblocking(False)
    global server_answer
    try:
        server_answer = client.s.recv(client.buf)
        server_answer = json.loads(server_answer)
        if server_answer['operation'] == 'send_mess':
            if isinstance(chat, ChatOpen):
                room = chat.get_room(server_answer['room'])
                user = server_answer['user']
                room['text'].insert(END, user, 'user')
                room['text'].insert(END, ': ' + server_answer['text'] + '\n')
                #print room['perm']
        elif server_answer['operation'] == 'change_user_status':
            if isinstance(chat, ChatOpen):
                chat.change_user_state(server_answer['users'])

        elif server_answer['operation'] == 'kick_user':
            if isinstance(chat, ChatOpen):
                chat.kick_user(server_answer['user'], server_answer['room'])

    except:
        root.after(1, loop_process)
        return
    root.after(1, loop_process)
    return


def the_exit():
    if isinstance(chat, ChatOpen):
        chat.exit()


if __name__ == "__main__":
    server_answer = {}
    chat = {}
    root = Tk()
    msg = StringVar()
    msg.set('')
    root.wm_title("myChat")
    obj = LoginForm()
    root.after(1, loop_process)
    root.protocol('WM_DELETE_WINDOW', the_exit)
    root.mainloop()
