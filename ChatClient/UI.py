#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict, Counter

__author__ = 'Vladimir Kanubrikov'

from Tkinter import *
from CustomComponents import UserList
import ttk
import client
import hashlib
import json
from settings import FONT_MULTIPLIER
import tkMessageBox

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
        self.q1 = Radiobutton(self.lf, text="Guest", variable=self.user_type, value=0,
                              command=self.change_user_type).grid(row=0, column=4)
        self.q2 = Radiobutton(self.lf, text="Normal", variable=self.user_type, value=1,
                              command=self.change_user_type).grid(row=0, column=3)

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
        global root, error_mes
        self.menu = Menu(root)
        root.config(menu=self.menu)
        self.fm = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.fm)

        data = client.json.loads(chat_data)
        print data
        if not data['user_reg']:
            self.fm.add_command(label='Registration...', command=self.registration)
            self.fm.add_separator()
        else:
            self.fm.add_command(label='Add new room...', command=self.add_new_room)

        self.fm.add_command(label='Exit', command=self.exit)

        self.chat = Frame(root)
        self.note = ttk.Notebook(self.chat)
        self.user = data['user_name']
        self.chat_rooms = {}
        self.login = data['user_login']

        root.wm_title("myChat (" + self.user + ")")

        for room in data['user_rooms']:
            self.add_room(room)

        self.note.pack()
        self.chat.pack()

        self.am = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Administrate room', menu=self.am)

        self.note.bind('<<NotebookTabChanged>>', self.admin_menu_act)
        self.note.bind('<<NotebookTabChanged>>', self.is_secure)
        self.am.add_command(label='Current room settings...', command=self.setup_room)

    def is_secure(self, event):
        print 'start is secure'
        room = self.get_active_room()
        if room.get('secure'):
            self.room_secure_test_pass(room.get('instance'), self.note.tab(self.note.select(), "text"))

    def delete_room_accept(self, room_name):
        room = self.get_room(room_name)
        self.note.forget(room['instance'])

    def delete_room(self):
        room_name = self.note.tab(self.note.select(), "text")
        room = self.get_active_room()
        if room.get('user_list').lenght() == 0:
            client.s.send(json.dumps({'operation': 'delete_room', 'room_name': room_name}))
        else:
            result = tkMessageBox.askquestion('Delete the "' + room_name + '" room', 'This room contents ' + str(
                room.get('user_list').lenght()) + ' users.\n Are you sure that you want to delete this room?',
                                              icon='warning')
            if result == 'yes':
                client.s.send(json.dumps({'operation': 'delete_room', 'room_name': room_name}))

    def setup_room(self):
        setup_room_dialog = Toplevel(self.chat)
        setup_room_dialog.title('Setup room')
        setup_room_dialog.l1 = Label(setup_room_dialog,
                                     text='"' + self.note.tab(self.note.select(), "text") + '" room settings:',
                                     font="Verdana " + font10)
        setup_room_dialog.room_name = self.note.tab(self.note.select(), "text")
        setup_room_dialog.mseq = IntVar()
        setup_room_dialog.new_pass = IntVar()
        setup_room_dialog.is_auth = IntVar()
        setup_room_dialog.l3 = Text(setup_room_dialog, font='Veranda ' + font10, height=8, width=32)
        setup_room_dialog.l2 = Label(setup_room_dialog, text='password:')
        setup_room_dialog.old_pass = Entry(setup_room_dialog, show='*')
        setup_room_dialog.old_pass_check = False
        setup_room_dialog.old_pass_typed = ''


        _s = ''
        _auth = ''
        _config_info = ''

        if self.get_active_room().get('secure'):
            _s = 'It\'s secure'
        else:
            _s = 'It\'s unsecure'
        if self.get_active_room().get('auth'):
            _auth = 'It\'s only for registered users'
        else:
            _auth = 'It\'s for all users'

        def update_info(_config_info):
            _text_info = 'The room has next settings now: \n ' + _s + '\n ' + _auth + '.' + '\n\nYour changes:\n ' + _config_info
            setup_room_dialog.l3.delete(1.0, END)
            setup_room_dialog.l3.insert(END, _text_info)

        update_info(_config_info)
        if self.get_active_room().get('secure'):
            setup_room_dialog.mseq.set(1)

        if self.get_active_room().get('auth'):
            setup_room_dialog.is_auth.set(1)

        def setup_init():
            if setup_room_dialog.is_auth.get():
                _ci = 'only for registered users'
                update_info(_ci)
            else:
                _ci = 'for all users'
                update_info(_ci)

            if self.get_active_room().get('secure'):
                setup_room_dialog.l2.grid(row=1, column=0)
                setup_room_dialog.old_pass.grid(row=1, column=1)
                setup_room_dialog.change_pass.grid(row=2, column=0, columnspan=3)
                if setup_room_dialog.mseq.get() and setup_room_dialog.new_pass.get():
                    update_info('new password' + '\n ' + _ci)
                    setup_room_dialog.npl.grid(row=3, column=0)
                    setup_room_dialog.np.grid(row=3, column=1, columnspan=2)
                    setup_room_dialog.npcl.grid(row=4, column=0)
                    setup_room_dialog.npc.grid(row=4, column=1, columnspan=2)

                else:
                    update_info('make unsecure' + '\n ' + _ci)
                    setup_room_dialog.npl.grid_forget()
                    setup_room_dialog.np.grid_forget()
                    setup_room_dialog.npcl.grid_forget()
                    setup_room_dialog.npc.grid_forget()
            else:
                if setup_room_dialog.mseq.get():
                    setup_room_dialog.new_pass.set(1)
                    update_info('make secure\n new password' + '\n ' + _ci)
                    setup_room_dialog.npl.grid(row=3, column=0)
                    setup_room_dialog.np.grid(row=3, column=1, columnspan=2)
                    setup_room_dialog.npcl.grid(row=4, column=0)
                    setup_room_dialog.npc.grid(row=4, column=1, columnspan=2)
                else:
                    update_info('' + _ci)
                    setup_room_dialog.new_pass.set(0)
                    setup_room_dialog.npl.grid_forget()
                    setup_room_dialog.np.grid_forget()
                    setup_room_dialog.npcl.grid_forget()
                    setup_room_dialog.npc.grid_forget()



        setup_room_dialog.auth = Checkbutton(setup_room_dialog, text='Only for registered users',
                                             variable=setup_room_dialog.is_auth, command=lambda: setup_init())
        setup_room_dialog.room_secure = Checkbutton(setup_room_dialog, text='room is secure',
                                                    variable=setup_room_dialog.mseq, command=lambda: setup_init())
        setup_room_dialog.change_pass = Checkbutton(setup_room_dialog, text='change password of this room',
                                                    variable=setup_room_dialog.new_pass, command=lambda: setup_init())
        setup_room_dialog.npl = Label(setup_room_dialog, text='New password:')
        setup_room_dialog.np = Entry(setup_room_dialog, show='*')
        setup_room_dialog.npcl = Label(setup_room_dialog, text='New password confirmation:')
        setup_room_dialog.npc = Entry(setup_room_dialog, show='*')
        setup_room_dialog.np.bind('<Button-1>', lambda a: refresh_state())
        setup_room_dialog.np.bind('<FocusIn>', lambda a: refresh_state())
        setup_room_dialog.npc.bind('<Button-1>', lambda a: refresh_state())
        setup_room_dialog.npc.bind('<FocusIn>', lambda a: refresh_state())

        setup_room_dialog.l1.grid(row=0, column=0, columnspan=3)
        setup_room_dialog.room_secure.grid(row=1, column=2)
        setup_room_dialog.auth.grid(row=5, column=0, columnspan=3)
        setup_room_dialog.l3.grid(row=6, column=0, columnspan=3)
        setup_room_dialog.button_ok = Button(setup_room_dialog, text='OK', command=lambda: self.send_new_settings(setup_room_dialog))
        setup_room_dialog.button_cancel = Button(setup_room_dialog, text='Cancel', command=setup_room_dialog.destroy)
        setup_room_dialog.button_ok.grid(row=7, column=0)
        setup_room_dialog.button_cancel.grid(row=7, column=2)

        if self.get_active_room().get('secure'):
            self.room_secure_test_pass(setup_room_dialog, setup_room_dialog.room_name)
            if setup_room_dialog.old_pass_check:
                setup_room_dialog.l2.grid(row=1, column=0)
                setup_room_dialog.old_pass.grid(row=1, column=1)
                setup_room_dialog.change_pass.grid(row=2, column=0, columnspan=3)
                setup_room_dialog.old_pass.insert(0, setup_room_dialog.old_pass_typed)

        setup_room_dialog.close = lambda: setup_room_dialog.destroy()

        def refresh_state():
            setup_room_dialog.np.configure(bg='white')
            setup_room_dialog.npc.configure(bg='white')

    def send_new_settings(self, settings):
        changes = []
        auth = settings.is_auth.get()
        secure = settings.mseq.get()
        change_pass = settings.new_pass.get()
        room_name = settings.room_name
        text = settings.l3.get("0.0", END).__str__()
        new_password = settings.np.get()
        new_password_c = settings.npc.get()
        old_password = settings.old_pass.get()
        old_pass = None
        new_pass = None

        if text.count('for all users') == 1 and text.count('only for registered users') == 1:
            changes.append('auth')
        if text.count('make secure') == 1:
            changes.append('secure')
        if text.count('new password') == 1:
            changes.append('change_pass')

        was_secure = self.get_active_room().get('secure')

        def check_conditions():

            if was_secure:
                old_password = settings.old_pass.get()
                if 'change_pass' in changes:
                    if new_password == new_password_c and new_password != '':
                        return True
                    else:
                        settings.np.configure(bg='red')
                        settings.npc.configure(bg='red')
                        return False
            else:
                old_password = None
                if 'change_pass' in changes:
                    if new_password == new_password_c and new_password != '':
                        return True
                    else:
                        settings.np.configure(bg='red')
                        settings.npc.configure(bg='red')
                        return False
                else:
                    if len(changes) != 0:
                        return True
                    else:
                        settings.close()
                        return False

        if check_conditions():
            if old_password != '' or old_password is not None:
                old_pass = hashlib.md5(old_password).hexdigest()
            else:
                old_pass = None

            if new_password != '' or new_password is not None:
                print new_password
                new_pass = hashlib.md5(new_password).hexdigest()

            else:
                new_pass = None

            mess = json.dumps({'operation': 'settings_room', 'changes': changes, 'room_name': room_name, 'auth': auth,
                               'secure': secure, 'change_pass': change_pass,
                               'old_pass': old_pass,
                               'new_pass': new_pass})
            client.s.send(mess)
            settings.close()

    def add_new_room(self):
        new_room_dialog = Toplevel(self.chat)
        new_room_dialog.title('Add new room')
        new_room_dialog.ln = Label(new_room_dialog, text='room name')
        #TODO: have to implement room settings
        new_room_dialog.name = Entry(new_room_dialog)
        new_room_dialog.button_ok = Button(new_room_dialog, text="OK",
                                           command=lambda: self.send_new_room_info(new_room_dialog))
        new_room_dialog.cancel = Button(new_room_dialog, text='Cancel', command=lambda: new_room_dialog.destroy())
        new_room_dialog.ln.grid(row=0, column=0)
        new_room_dialog.name.grid(row=0, column=1)
        new_room_dialog.button_ok.grid(row=1, column=0)
        new_room_dialog.cancel.grid(row=1, column=1)

    def send_new_room_info(self, dialog):
        mess = json.dumps({'operation': 'add_new_room', 'user_name': self.user, 'room_name': dialog.name.get()})
        client.s.send(mess)
        dialog.destroy()

    def add_user_to_the_room(self, user, room):
        if self.user == user:
            self.add_room(room)
        else:
            room_inst = self.get_room(str(room['room_name']))
            room_users = room_inst.get('user_list')
            assert isinstance(room_users, UserList)
            user = {user: room['users'][user]}
            room_users.user_add(user)

    def send_registration_form(self, form):
        if form.name.get() != form.password.get() and form.password.get() == form.password_conf.get():
            mess = json.dumps({'operation': 'registration', 'user_old_name': self.user, 'login': form.login.get(),
                               'user_new_name': form.name.get(), 'password': form.password.get()})
            client.s.send(mess)
            form.destroy()
        elif form.name.get() == form.password.get():
            form.password.configure(bg='red')
            form.name.configure(bg='red')
            error_mes.set("Name can't be equal password")
        elif form.login.get() == form.password.get():
            form.password.configure(bg='red')
            form.login.configure(bg='red')
            error_mes.set("Login can't be equal password")

        elif form.password_conf.get() != form.password.get():
            form.password.configure(bg='red')
            form.password_conf.configure(bg='red')
            error_mes.set("Password and Password confirmation should be equal")

    def registration(self):
        def back_to_normal(event):
            error_mes.set('')
            reg_dialog.name.configure(bg='white')
            reg_dialog.login.configure(bg='white')
            reg_dialog.password.configure(bg='white')

        reg_dialog = Toplevel(self.chat)
        reg_dialog.l1 = Label(reg_dialog, text='New Login: ')
        reg_dialog.login = Entry(reg_dialog)
        reg_dialog.login.delete(0, END)
        reg_dialog.login.insert(0, self.login)
        reg_dialog.l2 = Label(reg_dialog, text='New Name: ')
        reg_dialog.name = Entry(reg_dialog)
        reg_dialog.name.delete(0, END)
        reg_dialog.name.insert(0, self.user)
        reg_dialog.l3 = Label(reg_dialog, text='New Password \n(do not use username or login as password): ')
        reg_dialog.password = Entry(reg_dialog, show="*")
        reg_dialog.name.bind('<FocusIn>', func=back_to_normal)
        reg_dialog.name.bind('<Button-1>', func=back_to_normal)
        reg_dialog.login.bind('<FocusIn>', func=back_to_normal)
        reg_dialog.login.bind('<Button-1>', func=back_to_normal)
        reg_dialog.password.bind('<FocusIn>', func=back_to_normal)
        reg_dialog.password.bind('<Button-1>', func=back_to_normal)
        reg_dialog.l4 = Label(reg_dialog, text='Password Confirm: ')
        reg_dialog.password_conf = Entry(reg_dialog, show="*")
        reg_dialog.button_ok = Button(reg_dialog, text='OK', command=lambda: self.send_registration_form(reg_dialog))
        reg_dialog.button_cancel = Button(reg_dialog, text='Cancel', command=reg_dialog.destroy)
        reg_dialog.l1.grid(row=1, column=0)
        reg_dialog.l2.grid(row=2, column=0)
        reg_dialog.l3.grid(row=3, column=0)
        reg_dialog.l4.grid(row=4, column=0)
        reg_dialog.login.grid(row=1, column=1)
        reg_dialog.name.grid(row=2, column=1)
        reg_dialog.password.grid(row=3, column=1)
        reg_dialog.error_mes1 = Label(reg_dialog, textvariable=error_mes, foreground='red')
        reg_dialog.error_mes1.grid(row=0, column=0, columnspan=2, sticky=W)
        reg_dialog.password_conf.grid(row=4, column=1)
        reg_dialog.button_ok.grid(row=5, column=0)
        reg_dialog.button_cancel.grid(row=5, column=1)

    def user_reg(self, user_name_old, user_name):
        if self.user == user_name_old:
            info_window = Toplevel(self.chat)
            info_window.info = Label(info_window,
                                     text='Registration successful! Now the program it shutting. \n'
                                          'Next time you should login as normal user, using login and password '
                                          'which you were enter in registration form!')
            info_window.info.pack()
            info_window.button = Button(info_window, text='OK', command=self.exit)
            info_window.button.pack()
        else:
            for room in self.chat_rooms:
                room = self.chat_rooms.get(room)
                room_users = room.get('user_list')
                room_users.rename_user(user_name_old, user_name)

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

    def add_room(self, room):
        tab_inner = Frame(self.note, bg='#ffffff', bd=0)
        chat_window = Text(tab_inner, font="Arial " + font10, foreground='#666666', width=100, borderwidth=1,
                           relief=SUNKEN)
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
        if len(temp_list) > 0:
            temp_list.pop(self.user)
        user_list = UserList(tab_inner, str(room['room_name']), room['perm'], temp_list, self.user)
        user_list.grid(row=0, column=0, rowspan=2, sticky=W + N)
        self.chat_rooms.update(
            {room['room_name']: {'instance': tab_inner, 'perm': room['perm'], 'secure': room['secure'],
                                 'auth': room['auth'], 'text': chat_window,
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

    def add_new_room_to_user(self, user, room):
        if user == self.user:
            self.add_room(room)

    def is_admin(self):
        room = self.get_active_room()
        perm = room.get('perm')

        if self.note.tab(self.note.select(), "text") == 'default':
            try:
                index_item = self.am.index('Delete current room')
                self.am.delete(index_item)
            except:
                pass

            if perm.get('name') == 'root':
                return True
            else:
                return False
        else:
            if perm.get('name') == 'admin':
                try:
                    index_item = self.am.index('Delete current room')
                    self.am.delete(index_item)
                except:
                    pass

                self.am.add_command(label='Delete current room', command=self.delete_room)
                return True
            else:
                return False

    def admin_menu_act(self, event):
        if self.is_admin():
            self.menu.entryconfig(self.menu.index('Administrate room'), state=NORMAL)
        else:
            self.menu.entryconfig(self.menu.index('Administrate room'), state=DISABLED)

    def room_secure_test_pass(self, parent, room):
        check = Toplevel(parent)

        def close():
            check.destroy()
            parent.destroy()

        def send_pass(room, password, parent):
            client.s.send(json.dumps({'operation': 'check_room_pass', 'password': hashlib.md5(password).hexdigest(), 'room_name': room}))

            def take_answer():
                try:
                    sa = client.s.recv(client.buf)
                    sa = json.loads(sa)
                    if sa['operation'] == 'check_room_pass':
                        if sa['val']:
                            check.destroy()
                            parent.old_pass_check = sa['val']
                            parent.old_pass_typed = password
                        else:
                           close()

                except:
                    take_answer()
                    return

            take_answer()

        check.label = Label(check, text='password: ')
        check.password = Entry(check, show='*')
        check.ok = Button(check, text='OK', command=lambda: send_pass(room, check.password.get(), parent))
        check.cancel = Button(check, text='Cancel', command=lambda: close())

        check.label.grid(row=0, column=0)
        check.password.grid(row=0, column=1)
        check.ok.grid(row=1, column=0)
        check.cancel.grid(row=1, column=1)

        check.password.focus_set()
        check.transient(parent)
        check.grab_set()
        parent.wait_window(check)


def loop_process():
    """ Function which using for get messages and display the message in the chat window."""
    client.s.setblocking(False)
    global server_answer, root
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
                    chat.voting(server_answer['user'], server_answer['room'], server_answer['vote'],
                                server_answer['reason'])

            elif server_answer['operation'] == 'vote_complete':
                if isinstance(chat, ChatOpen):
                    chat.voting_complete(server_answer['user'], server_answer['room'])

            elif server_answer['operation'] == 'registration':
                if isinstance(chat, ChatOpen):
                    chat.user_reg(server_answer['user_old_name'], server_answer['user_new_name'])

            elif server_answer['operation'] == 'add_new_room':
                if isinstance(chat, ChatOpen):
                    chat.add_new_room_to_user(server_answer['user_name'], server_answer['room'])

            elif server_answer['operation'] == 'delete_room':
                if isinstance(chat, ChatOpen):
                    chat.delete_room_accept(server_answer['room_name'])

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
    error_mes = StringVar()
    error_mes.set('')
    msg.set('')
    root.wm_title("myChat")
    obj = LoginForm()
    root.after(1, loop_process)
    root.protocol('WM_DELETE_WINDOW', the_exit)
    root.mainloop()
