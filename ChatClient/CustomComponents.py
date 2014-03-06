#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
import os
from PIL import Image, ImageTk
from ToolTip import createToolTip
import client
import json

#TODO: special functionality for edit permissions
#TODO: make logic for work with server
#TODO: make component that can replace standard notepad component and will contents special functionality


class UserControl(Frame):
    def __init__(self, parent, room_name, perm, user, **options):
        Frame.__init__(self, parent, **options)
        assert isinstance(perm, dict)
        assert isinstance(room_name, str)

        self.label_width = 218

        # Import images
        _img_act = Image.open(os.path.dirname(__file__) + "/img/active.gif").resize((20, 20), Image.ANTIALIAS)
        _img_pass = Image.open(os.path.dirname(__file__) + "/img/disconect.gif").resize((20, 20), Image.ANTIALIAS)
        _img_cv = Image.open(os.path.dirname(__file__) + "/img/vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_dv = Image.open(os.path.dirname(__file__) + "/img/del_vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_edit = Image.open(os.path.dirname(__file__) + "/img/edit_perm.gif").resize((15, 15), Image.ANTIALIAS)
        _img_kick = Image.open(os.path.dirname(__file__) + "/img/kick.gif").resize((15, 15), Image.ANTIALIAS)

        self.room = room_name
        self._active = ImageTk.PhotoImage(_img_act)
        self._passive = ImageTk.PhotoImage(_img_pass)
        self.perm = perm
        self._cv = ImageTk.PhotoImage(_img_cv)
        self._dv = ImageTk.PhotoImage(_img_dv)
        self._edit = ImageTk.PhotoImage(_img_edit)
        self._kick = ImageTk.PhotoImage(_img_kick)
        self._address = user.get(user.keys()[0])
        self.parent = parent
        self.user_name = user.keys()[0]

        # setup configuration
        self.is_admin = ''
        client.s.send(json.dumps({'operation': 'is_admin', 'room': room_name, 'user': self.user_name}))
        sa = client.s.recv(client.buf)
        sa = re.sub('\}\{', '};{', sa)
        sa = re.split(';', sa)
        for answer_item in sa:
            server_answer = json.loads(answer_item)
            if isinstance(server_answer, dict):
                if server_answer["operation"] == 'is_admin':
                    self.is_admin = server_answer['val']
        self.configure(bg='#ffffff')
        self.create_vote = Button(self, image=self._cv, bg='white', bd=0)
        self.delete_vote = Button(self, image=self._dv, bg='white', bd=0)
        self.edit_perm = Button(self, image=self._edit, bg='white', bd=0)
        self.kick_user = Button(self, image=self._kick, bg='white', bd=0)
        self.name = ''
        self.display_user()

        self.kick_user.bind('<Button-1>', self.delete_user)

    def delete_user(self, event):
        client.s.send(json.dumps({'operation': 'kick_user', 'room': self.room, 'user': self.user_name}))

    def set_user_address(self, address):
        self._address = address
        self.display_user()

    def display_user(self):

        if self.perm['create_vote'] and self.is_admin != 'True':
            self.label_width -= 17
            self.create_vote.grid(row=0, column=2)
            createToolTip(self.create_vote, 'Create vote for kick this user from the room')

        if self.perm['delete_vote'] and self.is_admin != 'True':
            self.label_width -= 17
            self.delete_vote.grid(row=0, column=3)
            createToolTip(self.delete_vote, 'Delete vote for save this user in the room')

        if self.room != 'default':
            if self.perm['edit_perm']:
                self.label_width -= 17
                self.edit_perm.grid(row=0, column=4)
        else:
            if self.perm['edit_perm'] and self.perm['edit_perm_def']:
                self.label_width -= 17
                self.edit_perm.grid(row=0, column=4)

        createToolTip(self.edit_perm, 'Edit permissions for this user')

        if self.room != 'default':
            if self.perm['delete_user']:
                self.label_width -= 17
                self.kick_user.grid(row=0, column=5)
        else:
            if self.perm['delete_user'] and self.perm['edit_perm_def']:
                self.label_width -= 17
                self.kick_user.grid(row=0, column=5)
            elif self.perm['delete_user'] and self.is_admin != 'True':
                self.label_width -= 17
                self.kick_user.grid(row=0, column=5)

        createToolTip(self.kick_user, 'Kick this user')

        self.name = Label(self, text=' ' + self.user_name, bg='#ffffff', fg='#666666', width=self.label_width, anchor=W,
                          justify=LEFT,
                          font="Arial 8")

        self.name.grid(row=0, sticky=W + E + N + S)

        if self._address != '':
            self.name.configure(image=self._active, compound="left")
            createToolTip(self.name, 'User Name: ' + self.name.cget("text") + '\nUser Status: online')
        else:
            self.name.configure(image=self._passive, compound="left")
            createToolTip(self.name, 'User Name: ' + self.name.cget("text") + '\nUser Status: offline')


class UserList(Frame):
    def __init__(self, parent, room_name, perm, user_list, user, **options):
        Frame.__init__(self, parent, **options)

        assert isinstance(perm, dict)
        assert isinstance(user_list, dict)
        assert isinstance(room_name, str)

        self.user = user
        self.parent = parent
        self.users = {}

        for user in user_list:
            ul_user = UserControl(self, room_name, perm, {user: user_list.get(user)})
            self.users[user] = ul_user
            ul_user.pack(pady=(0, 1), padx=(0, 0))

        self.add_user = Button(self, text="Add new user into the room", bg='#ffffff', bd=0)

        if perm['add_user']:
            self.add_user.pack(fill=BOTH, expand=1)

        self.configure(bg="#999999")

    def change_user_state(self, user_list):
        assert isinstance(user_list, dict)
        for user in user_list:
            if user in self.users:
                self.users.get(user).set_user_address(user_list.get(user))
        for user in self.users:
            if not user in user_list:
                self.users.get(user).set_user_address('')

    def kick_user(self, user):
        if user in self.users:
            print self.users.get(user)
            self.users.get(user).destroy()