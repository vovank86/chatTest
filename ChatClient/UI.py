#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
from CustomComponents import UserList
import ttk
import client
import hashlib
import json
from settings import FONT_MULTIPLIER

#TODO: configure the Chat view using CustomComponents and grid

font10 = str(int(10 * FONT_MULTIPLIER))
font20 = str(int(20 * FONT_MULTIPLIER))



class LoginForm:
    def __init__(self):

        """
        Class constructor which using for creating Login Screen.
        @rtype : object
        """

        self.lf = Frame(root, padx=5, pady=5)
        self.lf.pack()
        self.title = Label(self.lf, text="myChat", font="Verdana " + font20)
        self.lab1 = Label(self.lf, text="Login:", font="Arial " + font10)
        self.user_name = Entry(self.lf, width=20, bd=1)
        self.user_name.bind('<Return>', self.focus_change)
        self.lab2 = Label(self.lf, text="Password:", font="Arial " + font10)
        self.password = Entry(self.lf, width=20, bd=1, show="*")
        self.password.bind('<Return>', self.focus_change)
        self.button_ok = Button(self.lf, text="Enter", command=self.send_data)
        self.button_cancel = Button(self.lf, text="Exit")
        self.button_cancel.bind("<Button-1>", LoginForm.exit_login)
        self.user_type = IntVar()
        self.q1 = Radiobutton(self.lf, text="Guest", variable=self.user_type, value=0, command=self.change_user_type).grid(row=0, column=4)
        self.q2 = Radiobutton(self.lf, text="Normal", variable=self.user_type, value=1, command=self.change_user_type).grid(row=0, column=3)


        self.title.grid(row=0, columnspan=2, pady=(0, 10))
        self.lab1.grid(row=1, sticky=W)

        self.user_name.grid(row=1, column=1, columnspan=3)
        self.change_user_type()

        self.button_ok.grid(row=4, columnspan=2, sticky=W + E + N + S, padx=(0, 2), pady=(30, 0))
        self.button_cancel.grid(row=4, columnspan=2, column=2, sticky=W + E + N + S, padx=(2, 0), pady=(30, 0))

        self.user_name.focus_set()

    def change_user_type(self):
        print 'change user type', self.user_type.get()

        if self.user_type.get():
            self.lab2.grid(row=2, sticky=W)
            self.password.grid(row=2, column=1, columnspan=3)
        else:
            self.lab2.grid_forget()
            self.password.grid_forget()

    def send_data(self):
        global server_answer, chat, chance
        if self.user_type.get():
            user_data = {"operation": "login", "user": self.user_name.get(),
                     "password": hashlib.md5(self.password.get()).hexdigest(), 'type': 'normal'}
        else:
            user_data = {"operation": "login", "user": self.user_name.get(),
                     "password": None, 'type': 'guest'}
        server_answer = client.connect(user_data)
        if not server_answer:
            root.destroy()
        else:
            self.lf.pack_forget()
            chat = ChatOpen(server_answer)

    @staticmethod
    def exit_login(event):
        client.s.close()
        root.destroy()

    def focus_change(self, event):
        if event.widget == self.user_name:
            self.password.focus_set()
        else:
            self.button_ok.invoke()


class ChatOpen():
    def __init__(self, chat_data):
        """
        Class constructor which using for creating user interface of chat system and display Chat Screen.
        @rtype : object
        """

        self.menu = Menu(root)
        root.config(menu=self.menu)
        fm = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=fm)


        data = client.json.loads(chat_data)
        print data
        if not data['user_reg']:
            fm.add_command(label='Registration...', command=self.registration)

        fm.add_command(label='Exit', command=self.exit)

        self.chat = Frame(root)
        self.note = ttk.Notebook(self.chat)
        self.user = data['user_name']
        self.chat_rooms = {}
        self.login = data['user_login']

        root.wm_title("myChat (" + self.user + ")")

        for room in data['user_rooms']:
            self.add_room(self.user, room)

        self.note.pack()
        self.chat.pack()

    def add_user_to_the_room(self, user, room):
        if self.user == user:
            self.add_room(self.user, room)
        else:
            room_inst = self.get_room(str(room['room_name']))
            room_users = room_inst.get('user_list')
            assert isinstance(room_users, UserList)
            user = {user: room['users'][user]}
            room_users.user_add(user)

    def registration(self):
        reg_dialog = Toplevel(self.chat)
        l1 = Label(reg_dialog, text='New Login: ')
        login = Entry(reg_dialog)
        login.delete(0, END)
        login.insert(0, self.login)
        l2 = Label(reg_dialog, text='New Name: ')
        name = Entry(reg_dialog)
        name.delete(0, END)
        name.insert(0, self.user)
        l3 = Label(reg_dialog, text='New Password: ')
        password = Entry(reg_dialog)
        l4 = Label(reg_dialog, text='Password Confirm: ')
        password_conf = Entry(reg_dialog)
        button_ok = Button(reg_dialog, text='OK')
        button_cancel = Button(reg_dialog, text='Cancel', command=reg_dialog.destroy)
        l1.grid(row=0, column=0)
        l2.grid(row=1, column=0)
        l3.grid(row=2, column=0)
        l4.grid(row=3, column=0)
        login.grid(row=0, column=1)
        name.grid(row=1, column=1)
        password.grid(row=2, column=1)
        password_conf.grid(row=3, column=1)
        button_ok.grid(row=4, column=0)
        button_cancel.grid(row=4, column=1)

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

        for room in self.chat_rooms:
            room = self.chat_rooms.get(room)
            room_users = room.get('user_list')
            room_users.change_user_state(users_info)

    def kick_user(self, user, room_name):
        room = self.get_room(room_name)
        room_users = room.get('user_list')
        room_users.kick_user(user)
        if self.user == user:
            self.note.forget(room['instance'])

    def add_room(self, user, room):
        tab_inner = Frame(self.note, bg='#ffffff', bd=0)
        chat_window = Text(tab_inner, font="Arial " + font10, foreground='#666666', width=100, borderwidth = 1, relief = SUNKEN)
        chat_window.tag_configure("user", foreground='#3399ff')
        chat_input = Entry(tab_inner, textvariable=msg, font="Arial " + font10, width=80)
        chat_send = Button(tab_inner, text="Send", relief=GROOVE, bd=1, bg="#19b3e5",
                           foreground='#ffffff', activebackground='#6cfcb3')
        chat_window.grid(row=0, column=1, columnspan=2)
        chat_input.grid(row=1, column=1, sticky=W + E + N + S)
        chat_send.grid(row=1, column=2, sticky=W + E + N + S)
        chat_send.bind('<Button-1>', self.send_process)
        chat_input.bind('<Return>', self.send_process)
        temp_list = room['users']
        temp_list.pop(self.user)
        user_list = UserList(tab_inner, str(room['room_name']), room['perm'], temp_list, self.user)
        user_list.grid(row=0, column=0, rowspan=2, sticky=W + N)
        self.chat_rooms.update(
            {room['room_name']: {'instance': tab_inner, 'perm': room['perm'], 'text': chat_window,
                                 'user_list': user_list}})

        self.note.add(tab_inner, text=room['room_name'])

        chat_input.focus_set()

    def voting(self, user_name, room_name, vote_id, reason):
        room = self.get_room(room_name)
        room_users = room.get('user_list')
        assert isinstance(room_users, UserList)
        room_users.voting(user_name, vote_id, reason)

    def voting_complete(self, user_name, room_name):
        room = self.get_room(room_name)
        room_users = room.get('user_list')
        assert isinstance(room_users, UserList)
        room_users.voting_complete(user_name)


def loop_process():
    """ Function which using for get messages and display the message in the chat window."""
    client.s.setblocking(False)
    global server_answer
    try:
        sa = client.s.recv(client.buf)
        sa = re.sub('\}\{', '};{', sa)
        sa = re.split(';', sa)

        for server_answer in sa:
            server_answer = json.loads(server_answer)
            if server_answer['operation'] == 'send_mess':
                if isinstance(chat, ChatOpen):
                    room = chat.get_room(server_answer['room'])
                    user = server_answer['user']
                    room['text'].insert(END, user, 'user')
                    room['text'].insert(END, ': ' + server_answer['text'] + '\n')

            elif server_answer['operation'] == 'change_user_status':
                if isinstance(chat, ChatOpen):
                    chat.change_user_state(server_answer['users'])

            elif server_answer['operation'] == 'kick_user':
                if isinstance(chat, ChatOpen):
                    chat.kick_user(server_answer['user'], server_answer['room'])

            elif server_answer['operation'] == 'add_user':
                if isinstance(chat, ChatOpen):
                    chat.add_user_to_the_room(server_answer['user'], server_answer['room'])

            elif server_answer['operation'] == 'start_vote':
                if isinstance(chat, ChatOpen):
                    print server_answer
                    chat.voting(server_answer['user'], server_answer['room'], server_answer['vote'], server_answer['reason'])

            elif server_answer['operation'] == 'vote_complete':
                if isinstance(chat, ChatOpen):
                    print server_answer
                    chat.voting_complete(server_answer['user'], server_answer['room'])

    except:
        root.after(1, loop_process)
        return

    root.after(1, loop_process)
    return


def the_exit():
    if isinstance(chat, ChatOpen):
        chat.exit()
    else:
        root.destroy()


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
