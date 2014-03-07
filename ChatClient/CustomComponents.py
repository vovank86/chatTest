#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
import os
from PIL import Image, ImageTk
from ToolTip import createToolTip
import client
import json
import ttk

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

        self.room = room_name
        self.user = user
        self.parent = parent
        self.users = {}

        self.add_user = AddUser(self)

        if perm['add_user']:
            self.add_user.pack(fill=BOTH, expand=1)

        for user in user_list:
            ul_user = UserControl(self, room_name, perm, {user: user_list.get(user)})
            self.users[user] = ul_user
            ul_user.pack(pady=(0, 1), padx=(0, 0))

        self.configure(bg="#999999")
        self.add_user_dialog = ''

        if self.users == {}:
            Label(self, text='Now this room doesn\'t has any users! '
                             '\n But if you are owner of this room,  than \nyou can add users.', justify='center',
                  bg='#ffffff', width=31, height=20,
                  foreground='#cccccc').pack(fill=BOTH, expand=1)

    def _add_user(self):
        self.add_user_dialog = Toplevel(self)


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


class AddUser(Frame):
    def __init__(self, parent, **options):
        Frame.__init__(self, parent, **options)
        self.users = ''
        self.perms = ''
        self.parent = parent
        self.users_found = self.users
        self.combo = ttk.Combobox(self, values=self.users_found, width=24)
        self.combo.bind('<FocusIn>', self.get_users)
        self.combo.bind('<KeyRelease>', self.autocomplete)
        self.add_button = Button(self, text='Add User', command=self.add_user, relief=RAISED, bd=0)
        self.combo.grid(row=0, column=0)
        self.add_button.grid(row=0, column=1)
        self.add_dialog = ''


    def add_user(self):
        self.add_dialog = Toplevel(self)
        self.add_dialog.name = Label(self.add_dialog, text=self.combo.get())
        self.add_dialog.name.grid(row=0, column=0, columnspan=2)
        self.add_dialog.perms = ttk.Combobox(self.add_dialog, values=self.perms)
        self.add_dialog.perms.bind('<FocusIn>', self.get_perms)
        perm_label = Label(self.add_dialog, text='Permissiohns: ')
        perm_label.grid(row=1, column=0)
        self.add_dialog.perms.grid(row=1, column=1)
        add_button = Button(self.add_dialog, text='Add', command=self.approve)
        close_button = Button(self.add_dialog, text='Cancel', command=self.add_dialog.destroy)
        add_button.grid(row=2, column=0)
        close_button.grid(row=2, column=1)
        self.add_dialog.perms.focus_set()

    def get_users(self, event):
        self.combo.unbind('<FocusIn>')
        client.s.send(json.dumps({'operation': 'get_users'}))

        def take_answer():
            try:
                sa = client.s.recv(client.buf)
                sa = json.loads(sa)
                if sa['operation'] == 'get_users':
                    self.users = sa['val']
                    self.users_found = self.users
                    self.combo['values'] = self.users_found

            except:
                take_answer()
                return

        take_answer()

    def get_perms(self, event):
        self.add_dialog.perms.unbind('<FocusIn>')
        client.s.send(json.dumps({'operation': 'get_perms'}))

        def take_answer():
            try:
                sa = client.s.recv(client.buf)
                sa = json.loads(sa)
                if sa['operation'] == 'get_perms':
                    self.perms = sa['val']
                    self.add_dialog.perms['values'] = self.perms

            except:
                take_answer()
                return

        take_answer()

    def autocomplete(self, event):
        char_typed = self.combo.get()
        users_found = []
        for item in self.users:
            if char_typed in item:
                users_found.append(item)
        self.combo['values'] = users_found

    def approve(self):
        client.s.send(json.dumps({'operation': 'add_user', 'user': self.add_dialog.name.cget('text'),
                                  'room': self.parent.room, 'perm': self.add_dialog.perms.get()}))
        self.add_dialog.destroy()







