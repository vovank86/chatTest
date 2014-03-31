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
import threading
from settings import FONT_MULTIPLIER

font8 = str(int(8 * FONT_MULTIPLIER))
font10 = str(int(10 * FONT_MULTIPLIER))
font20 = str(int(20 * FONT_MULTIPLIER))


class UserControl(Frame):
    def __init__(self, parent, room_name, perm, user, **options):
        Frame.__init__(self, parent, **options)
        assert isinstance(perm, dict)
        assert isinstance(room_name, str)

        # Import images
        _img_act = Image.open(os.path.dirname(__file__) + "/img/active.gif").resize((20, 20), Image.ANTIALIAS)
        _img_pass = Image.open(os.path.dirname(__file__) + "/img/disconect.gif").resize((20, 20), Image.ANTIALIAS)
        _img_cv = Image.open(os.path.dirname(__file__) + "/img/vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_dv = Image.open(os.path.dirname(__file__) + "/img/del_vote.gif").resize((15, 15), Image.ANTIALIAS)
        _img_edit = Image.open(os.path.dirname(__file__) + "/img/edit_perm.gif").resize((15, 15), Image.ANTIALIAS)
        _img_kick = Image.open(os.path.dirname(__file__) + "/img/kick.gif").resize((15, 15), Image.ANTIALIAS)
        _img_yes = Image.open(os.path.dirname(__file__) + "/img/yes.gif").resize((15, 15), Image.ANTIALIAS)
        _img_no = Image.open(os.path.dirname(__file__) + "/img/no.gif").resize((15, 15), Image.ANTIALIAS)

        self.room = room_name
        self._active = ImageTk.PhotoImage(_img_act)
        self._passive = ImageTk.PhotoImage(_img_pass)
        self.perm = perm
        self._cv = ImageTk.PhotoImage(_img_cv)
        self._dv = ImageTk.PhotoImage(_img_dv)
        self._edit = ImageTk.PhotoImage(_img_edit)
        self._kick = ImageTk.PhotoImage(_img_kick)
        self._yes = ImageTk.PhotoImage(_img_yes)
        self._no = ImageTk.PhotoImage(_img_no)
        self._address = user.get(user.keys()[0])
        self.parent = parent
        self.user_name = user.keys()[0]
        self.create_vote_dialog = ''
        self.edit_perm_dialog = ''
        self.vote_id = ''
        self.vote_reason = ''
        self.vote_timer = 60
        self.timer_inst = ''

        # setup configuration
        self.is_admin = ''
        client.s.send(json.dumps({'operation': 'is_admin', 'room': room_name, 'user': self.user_name}))

        def _is_admin():
            try:
                sa = client.s.recv(client.buf)
                sa = re.sub('\}\{', '};{', sa)
                sa = re.split(';', sa)
                for answer_item in sa:
                    server_answer = json.loads(answer_item)
                    if isinstance(server_answer, dict):
                        if server_answer["operation"] == 'is_admin':
                            self.is_admin = server_answer['val']
                return

            except:
                _is_admin()
                return

        _is_admin()

        self.configure(bg='#ffffff')
        self.create_vote = Button(self, image=self._cv, bg='white', bd=0, command=self.vote_create)
        self.delete_vote = Button(self, image=self._dv, bg='white', bd=0, command=self.vote_delete)
        self.edit_perm = Button(self, image=self._edit, bg='white', bd=0, command=self._edit_perm)
        self.kick_user = Button(self, image=self._kick, bg='white', bd=0, command=self.delete_user)
        self.name = ''
        self.voting_controls = Frame(self, bg='#f4f2f1', bd=0)
        self.vote_yes = Button(self.voting_controls, image=self._yes, bg='white', bd=0, command=self._vote_yes)
        self.vote_timer_label = Label(self.voting_controls, text=self.vote_timer, width=2)
        self.vote_no = Button(self.voting_controls, image=self._no, bg='white', bd=0, command=self._vote_no)

        self.display_user()

    def rename(self, user_name):
        client.logging.debug('start rename operation: old name = ' + self.user_name + ' new name = ' + user_name)
        self.user_name = user_name
        self.display_user()

    def delete_user(self):
        client.s.send(json.dumps({'operation': 'kick_user', 'room': self.room, 'user': self.user_name}))

    def set_user_address(self, address):
        self._address = address
        self.display_user()

    def display_user(self):
        if self.perm['create_vote'] and self.is_admin != 'True':
            self.create_vote.grid(row=0, column=2)
            createToolTip(self.create_vote, 'Create vote for kick this user from the room')

        if self.perm['delete_vote'] and self.is_admin != 'True':
            self.delete_vote.grid(row=0, column=3)
            createToolTip(self.delete_vote, 'Delete vote for save this user in the room')
            if self.vote_id == '':
                self.delete_vote.config(state='disabled')

        if self.room != 'default':
            if self.perm['edit_perm']:
                self.edit_perm.grid(row=0, column=4)
        else:
            if self.perm['edit_perm'] and self.perm['edit_perm_def']:
                self.edit_perm.grid(row=0, column=4)

        createToolTip(self.edit_perm, 'Edit permissions for this user')

        if self.room != 'default':
            if self.perm['delete_user']:
                self.kick_user.grid(row=0, column=5)
        else:
            if self.perm['delete_user'] and self.perm['edit_perm_def']:
                self.kick_user.grid(row=0, column=5)
            elif self.perm['delete_user'] and self.is_admin != 'True' and self.perm['edit_perm_def']:
                self.kick_user.grid(row=0, column=5)
            else:
                pass

        createToolTip(self.kick_user, 'Kick this user')

        if self.vote_id != '':
            self.vote_yes.config(state='normal')
            self.vote_no.config(state='normal')
            self.delete_vote.config(state='normal')
            self.create_vote.config(state='disabled')
            self.voting_controls.grid(row=0, column=6, columnspan=3, padx=(0, 2))
            self.vote_yes.grid(row=0, column=1, padx=(2, 0))
            createToolTip(self.vote_yes,
                          'Click if you agree to kick this user according with reason.\nReason: ' + self.vote_reason)
            self.vote_no.grid(row=0, column=2, padx=(1, 0))
            createToolTip(self.vote_no,
                          'Click if you disagree to kick this user according with reason.\nReason: ' + self.vote_reason)

            self.vote_timer_label.grid(row=0, column=3, padx=(2, 2))
            createToolTip(self.vote_timer_label, 'remaining time')

        self.name = Label(self, text=' ' + self.user_name, bg='#ffffff', fg='#666666', width=150, anchor=W,
                          justify=LEFT,
                          font="Arial " + font8)

        self.name.grid(row=0, sticky=W + E + N + S)

        if self._address != '':
            self.name.configure(image=self._active, compound="left")
            createToolTip(self.name, 'User Name: ' + self.name.cget("text") + '\nUser Status: online')
        else:
            self.name.configure(image=self._passive, compound="left")
            createToolTip(self.name, 'User Name: ' + self.name.cget("text") + '\nUser Status: offline')

    def vote_create(self):
        self.create_vote_dialog = Toplevel(self)
        info = Label(self.create_vote_dialog,
                     text='Please type why do you want to kick user: ' + self.user_name + ' from this room:')
        info.grid(row=0, column=0, columnspan=2)
        self.create_vote_dialog.reason = Entry(self.create_vote_dialog)
        self.create_vote_dialog.reason.grid(row=1, column=0, columnspan=2)
        button_ok = Button(self.create_vote_dialog, text='Start', command=self.start_vote)
        button_cancel = Button(self.create_vote_dialog, text='Cancel', command=self.create_vote_dialog.destroy)
        button_ok.grid(row=2, column=0)
        button_cancel.grid(row=2, column=1)

    def start_vote(self):
        client.s.send(json.dumps({'operation': 'start_vote', 'user': self.user_name, 'room': self.room,
                                  'reason': self.create_vote_dialog.reason.get()}))
        self.create_vote_dialog.destroy()

    def voting(self, vote_id, reason):
        self.vote_timer = 60
        self.vote_id = vote_id
        self.vote_reason = reason
        self.display_user()

        def go():
            self.vote_timer -= 1
            self.vote_timer_label.configure(text=self.vote_timer)
            if self.vote_timer > 0:
                self.timer_inst = threading.Timer(1.0, go)
                self.timer_inst.start()

        self.timer_inst = threading.Timer(1.0, go)
        self.timer_inst.start()

    def vote_delete(self):
        client.s.send(json.dumps({'operation': 'vote_cancel', 'vote': self.vote_id, 'user': self.user_name,
                                  'room': self.room}))
        self.voting_complete()

    def _vote_yes(self):
        client.s.send(json.dumps({'operation': 'voting', 'vote': self.vote_id, 'val': True}))
        self.vote_yes.config(state='disabled')
        self.vote_no.config(state='disabled')

    def _vote_no(self):
        client.s.send(json.dumps({'operation': 'voting', 'vote': self.vote_id, 'val': False}))
        self.vote_yes.config(state='disabled')
        self.vote_no.config(state='disabled')

    def voting_complete(self):
        self.vote_id = ''
        self.delete_vote.config(state='disabled')
        self.timer_inst.cancel()
        self.vote_yes.grid_forget()
        self.vote_no.grid_forget()
        self.voting_controls.grid_forget()
        self.create_vote.config(state='normal')

    def _edit_perm(self):
        self.edit_perm_dialog = Toplevel(self)
        self.edit_perm_dialog.title('Edit permissions for ' + self.user_name)
        self.edit_perm_dialog.perm = ''
        self.edit_perm_dialog.perms = ''
        client.s.send(json.dumps({'operation': 'get_perm', 'user': self.user_name, 'room': self.room}))

        def get_perm_for_user():
            try:
                sa = client.s.recv(client.buf)
                sa = json.loads(sa)
                if sa['operation'] == 'get_perm':
                    self.edit_perm_dialog.perm = sa['val']

            except:
                get_perm_for_user()
                return

        get_perm_for_user()

        Label(self.edit_perm_dialog, text='Permissions for user "' + self.user_name + '" now:').grid(row=0, column=0)
        Label(self.edit_perm_dialog, text=self.edit_perm_dialog.perm, foreground='red').grid(row=0, column=1)

        client.s.send(json.dumps({'operation': 'get_perms', 'user': self.user_name}))

        def get_perms():
            try:
                sa = client.s.recv(client.buf)
                sa = json.loads(sa)
                if sa['operation'] == 'get_perms':
                    self.edit_perm_dialog.perms = sa['val']

            except:
                get_perms()
                return

        get_perms()

        Label(self.edit_perm_dialog, text='New permissions for user "' + self.user_name + '":').grid(row=1, column=0)
        self.edit_perm_dialog.perms_combo = ttk.Combobox(self.edit_perm_dialog, values=self.edit_perm_dialog.perms)
        self.edit_perm_dialog.perms_combo.current(self.edit_perm_dialog.perms.index(self.edit_perm_dialog.perm))
        self.edit_perm_dialog.perms_combo.grid(row=1, column=1)
        Button(self.edit_perm_dialog, text='OK', command=self.set_new_perm).grid(row=2, column=0)
        Button(self.edit_perm_dialog, text='Cancel', command=self.edit_perm_dialog.destroy).grid(row=2, column=1)


    def set_new_perm(self):
        new_perm = self.edit_perm_dialog.perms_combo.get()
        client.s.send(
            json.dumps({'operation': 'set_perm', 'user': self.user_name, 'room': self.room, 'perm': new_perm}))
        self.edit_perm_dialog.destroy()
        if new_perm == 'admin':
            self.is_admin = 'True'
            self.create_vote.grid_forget()
            self.delete_vote.grid_forget()
        else:
            self.is_admin = 'False'

        self.display_user()


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
        self.perm = perm
        self.user_empty_informer = Label(self, text='Now this room doesn\'t has any users! '
                                                    '\n But if you are owner of this room,  than \nyou can add users.',
                                         justify='center',
                                         bg='#ffffff', foreground='#cccccc', height=10)

        self.add_user = AddUser(self)
        if perm['add_user'] and self.room != 'default':
            self.add_user.pack(fill=BOTH, expand=1)

        for user in user_list:
            user_obj = {user: user_list.get(user)}
            self.user_add(user_obj)

        self.configure(bg="#999999")
        self.add_user_dialog = ''

        if self.users == {}:
            self.user_empty_informer.pack(fill=BOTH, expand=1, padx=(0, 0), pady=(0, 0))

    def _add_user(self):
        self.add_user_dialog = Toplevel(self)

    def rename_user(self, old_name, new_name):
        user = self.users.get(old_name)
        self.users[new_name] = self.users.pop(old_name)
        user.rename(new_name)

    def change_user_state(self, user_list):
        assert isinstance(user_list, dict)
        for user in user_list:
            if user in self.users:
                self.users.get(user).set_user_address(user_list.get(user))

            elif self.user != user and self.room == 'default':
                #print user
                user = {user: user_list.get(user)}
                self.user_add(user)
        for user in self.users:
            if not user in user_list:
                self.users.get(user).set_user_address('')

    def user_add(self, user_info):
        user = user_info.keys()[0]
        ul_user = UserControl(self, self.room, self.perm, user_info)
        if len(self.users) == 0:
            informer_packed = 1
        else:
            informer_packed = 0
        self.users[user] = ul_user
        if len(self.users) > 0 and informer_packed:
            self.user_empty_informer.pack_forget()
        ul_user.pack(pady=(0, 1), padx=(0, 0), fill=BOTH, expand=1)

    def kick_user(self, user):
        if user in self.users:
            kicked_user = self.users.pop(user)
            kicked_user.destroy()
            if len(self.users) == 0:
                self.user_empty_informer.pack()

    def voting(self, user_name, vote_id, reason):
        if user_name in self.users:
            user = self.users.get(user_name)
            user.voting(vote_id, reason)

    def voting_complete(self, user_name):
        if user_name in self.users:
            user = self.users.get(user_name)
            assert isinstance(user, UserControl)
            user.voting_complete()

    def lenght(self):
        return len(self.users)


class AddUser(Frame):
    def __init__(self, parent, **options):
        Frame.__init__(self, parent, **options)
        self.users = ''
        self.perms = ''
        self.parent = parent
        self.users_found = self.users
        self.combo = ttk.Combobox(self, values=self.users_found, width=24)
        self.combo.bind('<FocusIn>', self.get_users)
        self.combo.bind('<Button-1>', self.get_users)
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
        client.s.send(json.dumps({'operation': 'get_users', 'room': self.parent.room}))

        if event.widget.cget('state').__str__() != 'disabled':
            def take_answer():
                try:
                    sa = client.s.recv(client.buf)
                    sa = json.loads(sa)
                    if sa['operation'] == 'get_users':
                        if sa['val']:
                            self.combo.config(state='normal')
                            self.add_button.config(state='normal')
                            self.users = sa['val']
                            self.users_found = self.users
                            self.combo['values'] = self.users_found
                        else:
                            self.combo.config(state='disabled')
                            self.add_button.config(state='disabled')

                except:
                    take_answer()
                    return

            take_answer()

    def get_perms(self, event):
        self.add_dialog.perms.unbind('<FocusIn>')
        client.s.send(json.dumps({'operation': 'get_perms', 'user': self.add_dialog.name.cget('text')}))

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
        self.combo.set('')