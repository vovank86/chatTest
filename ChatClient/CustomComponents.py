#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
import os
from PIL import Image, ImageTk

#TODO: special functionality for edit permissions
#TODO: make logic for work with server

#perm = {
#    u'create_vote': 1, u'_labels': [u'id', u'name', u'add_user', u'create_room', u'create_vote',
#                                    u'delete_room', u'delete_user', u'delete_vote', u'make_secure', u'make_unsecure',
#                                    u'voting', u'edit_perm',
#                                    u'default_edit'], u'delete_vote': 1, u'name': u'root', u'delete_room': 1,
#    u'make_secure': 1, u'delete_user': 1,
#    u'create_room': 1, u'add_user': 1, u'voting': 1, u'id': 1, u'make_unsecure': 1, u'edit_perm': 1,
#    u'default_edit': 1
#}
#
#users = {'Vladimir Kanubrikov': ('127.0.0.1', '63945'), 'Daddy': ('127.0.0.1', '63946'), 'Pupkin': ''}
#

class UserControl(Frame):
    def __init__(self, parent, room_name, perm, user, **options):
        Frame.__init__(self, parent, **options)
        assert isinstance(perm, dict)
        assert isinstance(room_name, str)

        # Import images
        _img_act = Image.open(os.path.dirname(__file__) + "/img/active.gif").resize((20, 20), Image.ANTIALIAS)
        _img_pass = Image.open(os.path.dirname(__file__) + "/img/disconect.gif").resize((20, 20), Image.ANTIALIAS)
        _img_private = Image.open(os.path.dirname(__file__) + "/img/privat_mess.gif").resize((15, 15), Image.ANTIALIAS)
        _img_cv = Image.open(os.path.dirname(__file__) + "/img/vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_dv = Image.open(os.path.dirname(__file__) + "/img/del_vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_edit = Image.open(os.path.dirname(__file__) + "/img/edit_perm.gif").resize((15, 15), Image.ANTIALIAS)
        _img_kick = Image.open(os.path.dirname(__file__) + "/img/kick.gif").resize((15, 15), Image.ANTIALIAS)

        self._active = ImageTk.PhotoImage(_img_act)
        self._passive = ImageTk.PhotoImage(_img_pass)
        self._pm = ImageTk.PhotoImage(_img_private)
        self._cv = ImageTk.PhotoImage(_img_cv)
        self._dv = ImageTk.PhotoImage(_img_dv)
        self._edit = ImageTk.PhotoImage(_img_edit)
        self._kick = ImageTk.PhotoImage(_img_kick)
        self._address = user.get(user.keys()[0])

        # setup configuration
        self.configure(bg='#ffffff')
        self.name = Label(self, text=' ' + user.keys()[0], bg='#ffffff', fg='#666666', width=150, anchor=W,
                          justify=LEFT,
                          font="Arial 8")
        self.send_private_mess = Button(self, image=self._pm, bg='white', bd=0)
        self.create_vote = Button(self, image=self._cv, bg='white', bd=0)
        self.delete_vote = Button(self, image=self._dv, bg='white', bd=0)
        self.edit_perm = Button(self, image=self._edit, bg='white', bd=0)
        self.kick_user = Button(self, image=self._kick, bg='white', bd=0)

        # print user
        self.print_user()
        self.name.grid(row=0, sticky=W + E + N + S)
        self.send_private_mess.grid(row=0, column=1)

        if perm['create_vote']:
            self.create_vote.grid(row=0, column=2)

        if perm['delete_vote']:
            self.delete_vote.grid(row=0, column=3)

        if perm['edit_perm']:
            self.edit_perm.grid(row=0, column=4)

        if perm['delete_user']:
            self.kick_user.grid(row=0, column=5)

    def set_user_address(self, address):
        self._address = address
        self.print_user()

    def print_user(self):
        if self._address != '':
            self.name.configure(image=self._active, compound="left")
        else:
            self.name.configure(image=self._passive, compound="left")
            self.send_private_mess.configure(state=DISABLED)


class UserList(Frame):
    def __init__(self, parent, room_name, perm, user_list, **options):
        Frame.__init__(self, parent, **options)

        assert isinstance(perm, dict)
        assert isinstance(user_list, dict)
        assert isinstance(room_name, str)
        self.users = {}
        for user in user_list:
            ul_user = UserControl(self, room_name, perm, {user: user_list.get(user)})
            self.users[user] = ul_user
            ul_user.pack(pady=(0, 1), padx=(1, 0))

        self.add_user = Button(self, text="Add new user into the room", bg='#ffffff', bd=0)
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

#TODO: When components will complete kill these rows:
#root = Tk()
#root.overrideredirect(False)
#root.wm_title("test")
#obj = UserList(root, 'default', perm, users)
#obj.pack()
#root.mainloop()

