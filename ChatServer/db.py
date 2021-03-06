#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from getpass import *
import hashlib
import sys
import settings
import time
import logging

logging.basicConfig(format=settings.LOGGING['FORMAT'], level=logging.DEBUG, filename=settings.LOGGING['FILE'])


if sys.platform == 'win32':
    database = settings.DATABASES['default']
else:
    database = settings.DATABASES['unix']

engine = create_engine(database['ENGINE'] + database['ROUTE'] + database['NAME'], echo=database['DEBUG_MODE'])
Base = declarative_base()


class Associations(Base):
    __tablename__ = 'associations'

    room_id = Column(Integer, ForeignKey('room.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    perm_id = Column(Integer, ForeignKey('perm.id'))
    perm = relationship("Perm")
    user = relationship("User", backref='room_assocs')


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    auth = Column(Integer(1))
    password = Column(String(40))
    secure = Column(Integer(1))
    user = relationship("Associations", backref='room')
    vote = relationship("Vote")

    def __init__(self, name):
        self.name = name
        self.auth = 0
        self.secure = 0

    def is_only_auth(self):
        return self.auth

    def is_secure(self):
        return self.secure


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    registered = Column(Integer(1))
    name = Column(String(50), unique=True)
    password = Column(String(40))
    login = Column(String(30))
    vote = relationship("Vote")

    def __init__(self, login, name, password, registered):
        self.login = login
        self.name = name
        self.password = password
        self.registered = registered


class Perm(Base):
    __tablename__ = 'perm'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    create_room = Column(Integer(1))
    delete_room = Column(Integer(1))
    create_vote = Column(Integer(1))
    delete_vote = Column(Integer(1))
    voting = Column(Integer(1))
    make_secure = Column(Integer(1))
    make_unsecure = Column(Integer(1))
    add_user = Column(Integer(1))
    delete_user = Column(Integer(1))
    edit_perm = Column(Integer(1))
    edit_perm_def = Column(Integer(1))


    def __init__(self, name, create_room, delete_room, create_vote, delete_vote, voting, make_secure, make_unsecure,
                 add_user,
                 delete_user, edit_perm, edit_perm_def):
        self.name = name
        self.create_room = create_room
        self.delete_room = delete_room
        self.create_vote = create_vote
        self.delete_vote = delete_vote
        self.edit_perm = edit_perm
        self.edit_perm_def = edit_perm_def
        self.voting = voting
        self.make_secure = make_secure
        self.make_unsecure = make_unsecure
        self.add_user = add_user
        self.delete_user = delete_user


class Vote(Base):
    __tablename__ = 'vote'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    summary_vote = Column(Integer)
    vote_yes = Column(Integer)
    vote_no = Column(Integer)
    start_time = Column(String(40))
    end_time = Column(String(40))

    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id
        self.summary_vote = 0
        self.vote_yes = 0
        self.vote_no = 0
        self.start_time = time.strftime("%d %b %Y %H:%M:%S %Z", time.localtime())
        self.end_time = ''

    def __vote_yes__(self):
        self.vote_yes += 1

    def __vote_no__(self):
        self.vote_no += 1

    def get_result(self):
        self.end_time = time.strftime("%d %b %Y %H:%M:%S %Z", time.localtime())
        self.summary_vote = self.vote_yes - self.vote_no
        if self.summary_vote > 0:
            return True
        else:
            return False


Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)


def make_server_password():
    """
    @rtype : str
    """
    temp_password = getpass(prompt="Please type your password:")
    temp_password2 = getpass(prompt="Confirm your password:")
    if temp_password == temp_password2:
        temp_password = hashlib.md5(temp_password).hexdigest()
        return temp_password
    else:
        make_server_password()


def install_chat(session, PORT):
    """
    This is a procedure for first setup chat application.
    It use the command line for setup first user - root user, whom will has fool permissions.

    """
    print "It's first run of the CHAT SERVER.\nSo you need to answer few questions..."
    login = raw_input('Please type the nick-name (Login) of the root user: ')
    name = raw_input('\nPlease type your fool name (Screen Name):')
    password = make_server_password()

    root_perm = Perm("root", 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    admin_perm = Perm("admin", 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0)
    authorised_perm = Perm("auth_user", 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0)
    guest_perm = Perm("guest", 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)

    default_room = Room("default")
    a = Associations()
    a.user = User(login, name, password, 1)
    a.perm = root_perm
    default_room.user.append(a)
    session.add(a)
    session.add(root_perm)
    session.add(admin_perm)
    session.add(authorised_perm)
    session.add(guest_perm)
    session.add(default_room)

    session.commit()
    session.close()

    print "\nThanks."
    print "\nChat server started on port " + str(PORT)
    logging.info('chat was installed')


def auth_user(login, password, type):
    """
    @rtype : object
    """
    session = Session()
    users = session.query(User).order_by(User.id)
    users_logins = []
    for instance in users:
        users_logins.append(instance.login)
    for instance in users:
        if login in users_logins and login == instance.login:
            user = instance
            if not check_pass(user, password):
                return False
            else:
                return start_sys(user, session)

        elif not login in users_logins:
            if type == 'guest':
                default_room = session.query(Room).filter(Room.name == 'default').one()
                guest_perm = session.query(Perm).filter(Perm.name == 'guest').one()
                a = Associations()
                a.user = User(login, login, None, 0)
                u = a.user
                a.perm = guest_perm
                default_room.user.append(a)
                session.add(a)
                session.commit()
                return start_sys(u, session)
        else:
            continue

    session.commit()
    session.close()


def check_pass(user, password):
    if password == user.password:
        return user
    else:
        return False


def registration(login, new_login, new_name, new_password):
    session_reg = Session()
    user = session_reg.query(User).filter(User.login.in_([login])).one()
    user.password = hashlib.md5(new_password).hexdigest()
    user.registered = 1
    user.login = new_login
    user.name = new_name
    auth_perm = session_reg.query(Perm).filter(Perm.name == 'auth_user').one()
    room = session_reg.query(Room).filter(Room.name == 'default').one()
    a = session_reg.query(Associations).filter(
        Associations.user_id == user.id, Associations.room_id == room.id).one()
    a.perm = auth_perm
    session_reg.commit()
    session_reg.close()


def is_admin(uname, room):
    session_ia = Session()
    u = session_ia.query(User.id).filter(User.name == uname).scalar()
    r = session_ia.query(Room.id).filter(Room.name == room).scalar()
    p = session_ia.query(Associations.perm_id).filter(Associations.room_id == r, Associations.user_id == u).scalar()
    p_name = session_ia.query(Perm.name).filter(Perm.id == p).scalar()
    if p_name == 'admin' or p_name == 'root':
        return 'True'
    else:
        return 'False'
    session_ia.commit()
    session_ia.close()


def start_sys(user, session):
    """
    This function return data for UI initialisation.
    @param user
    """
    user_rooms = []
    rooms = session.query(Room).all()
    for room in rooms:
        room_users = []
        for r_user in room.user:
            room_users.append(session.query(User.name).filter(User.id == r_user.user_id).scalar())

        for r_user in room.user:

            if r_user.user_id == user.id:
                the_room = dict(room_name=room.name,
                                perm=session.query(Perm.id, Perm.name, Perm.add_user, Perm.create_room,
                                                   Perm.create_vote, Perm.delete_room, Perm.delete_user,
                                                   Perm.delete_vote, Perm.make_secure, Perm.make_unsecure,
                                                   Perm.voting, Perm.edit_perm, Perm.edit_perm_def).filter(
                                    Perm.id == r_user.perm_id).one().__dict__,
                                users=room_users, secure=room.secure, auth=room.auth)
                user_rooms.append(the_room)

    start_chat_system = {"user_login": user.login, "user_name": user.name, "user_reg": user.registered,
                         "user_rooms": user_rooms}
    return start_chat_system


def kick_user(user, room):
    session_ku = Session()
    u = session_ku.query(User.id).filter(User.name == user).scalar()
    r = session_ku.query(Room.id).filter(Room.name == room).scalar()

    if room == 'default':
        user = session_ku.query(User).get(u)
        assoc_all = session_ku.query(Associations).filter(Associations.user_id == u).all()
        rooms = []
        for a in assoc_all:
            rooms.append(session_ku.query(Room.name).filter(Room.id == a.room_id).scalar())
            session_ku.delete(a)
        session_ku.delete(user)
        session_ku.commit()
        return rooms
    else:
        assoc = session_ku.query(Associations).filter(Associations.room_id == r, Associations.user_id == u).delete()

    session_ku.commit()
    session_ku.close()
    return assoc


def get_users(room_name):
    session_get_users = Session()
    users = []
    room = session_get_users.query(Room).filter(Room.name == room_name).one()
    room_users = []
    for assoc in room.user:
        room_users.append(session_get_users.query(User).get(assoc.user_id).name)

    if room.is_only_auth():
        for user in session_get_users.query(User.name).filter(User.registered == 1).all():
            if not user[0] in room_users:
                users.append(user[0])
    else:
        for user in session_get_users.query(User.name).all():
            if not user[0] in room_users:
                users.append(user[0])

    if len(users) > 0:
        return users
    else:
        return False
    session_get_users.commit()
    session_get_users.close()


def get_perms(user_name):
    session_get_perms = Session()
    user_reg = session_get_perms.query(User.registered).filter(User.name == user_name).scalar()
    perms = []
    for perm in session_get_perms.query(Perm.name).all():
        if perm[0] != 'root' and user_reg:
            perms.append(perm[0])
        elif perm[0] != 'root' and not user_reg:
            if perm[0] == 'guest':
                perms.append(perm[0])

    return perms
    session_get_perms.commit()
    session_get_perms.close()


def get_perm_for_user(user_name, room_name):
    session_get_perm = Session()
    room_id = session_get_perm.query(Room.id).filter(Room.name == room_name).scalar()
    user_id = session_get_perm.query(User.id).filter(User.name == user_name).scalar()
    perm = session_get_perm.query(Associations).filter(Associations.room_id == room_id, Associations.user_id == user_id).one()
    perm = perm.perm.name
    return perm


def set_perm_for_user(user_name, room_name, perm_name):
    session_set_perm = Session()
    room_id = session_set_perm.query(Room.id).filter(Room.name == room_name).scalar()
    user_id = session_set_perm.query(User.id).filter(User.name == user_name).scalar()
    new_perm = session_set_perm.query(Perm.id).filter(Perm.name == perm_name).scalar()
    perm = session_set_perm.query(Associations).filter(Associations.room_id == room_id, Associations.user_id == user_id).delete()
    assoc = Associations()
    assoc.user_id = user_id
    assoc.room_id = room_id
    assoc.perm_id = new_perm
    session_set_perm.add(assoc)
    session_set_perm.commit()
    session_set_perm.close()
    return perm


def add_u_to_the_r(uname, room_name, perm_name):
    session = Session()
    new_u = Associations()
    user = session.query(User.id).filter(User.name == uname).scalar()
    room = session.query(Room.id).filter(Room.name == room_name).scalar()
    perm = session.query(Perm.id).filter(Perm.name == perm_name).scalar()

    new_u.user_id = user
    new_u.perm_id = perm
    new_u.room_id = room
    session.add(new_u)
    session.commit()

    room_obj = session.query(Room).get(room)
    room_users = []
    the_room = {}
    for r_user in room_obj.user:
        room_users.append(session.query(User.name).filter(User.id == r_user.user_id).one()[0])
    for r_user in room_obj.user:
        if r_user.user_id == user:
            the_room = dict(room_name=room_obj.name,
                            perm=session.query(Perm.id, Perm.name, Perm.add_user, Perm.create_room,
                                               Perm.create_vote, Perm.delete_room, Perm.delete_user,
                                               Perm.delete_vote, Perm.make_secure, Perm.make_unsecure,
                                               Perm.voting, Perm.edit_perm, Perm.edit_perm_def).filter(
                                Perm.id == r_user.perm_id).one().__dict__,
                            users=room_users, secure=room_obj.secure, auth=room_obj.auth)
    add_user_obj = {"user_name": uname, "room": the_room}

    session.close()
    return add_user_obj


def create_vote(user_name, room_name):
    session_vote = Session()
    user = session_vote.query(User.id).filter(User.name == user_name).scalar()
    room = session_vote.query(Room.id).filter(Room.name == room_name).scalar()
    vote = Vote(room, user)
    session_vote.add(vote)
    session_vote.commit()
    return vote.id
    session_vote.close()


def send_result_of_vote(vote_id):
    session_vote_res = Session()
    vote = session_vote_res.query(Vote).get(vote_id)
    result = vote.get_result()
    session_vote_res.add(vote)
    session_vote_res.commit()
    session_vote_res.close()
    return result


def vote_yes(vote_id):
    session_vote_yes = Session()
    vote = session_vote_yes.query(Vote).get(vote_id)
    vote.__vote_yes__()
    session_vote_yes.add(vote)
    session_vote_yes.commit()
    session_vote_yes.close()


def vote_no(vote_id):
    session_vote_no = Session()
    vote = session_vote_no.query(Vote).get(vote_id)
    vote.__vote_no__()
    session_vote_no.add(vote)
    session_vote_no.commit()
    session_vote_no.close()


def vote_cancel(vote_id):
    session_vote_cancel = Session()
    res = session_vote_cancel.query(Vote).filter(Vote.id == vote_id).delete()
    session_vote_cancel.commit()
    session_vote_cancel.close()
    return res


def add_new_room(user_name, room_name):
    session_add_new_room = Session()
    user = session_add_new_room.query(User).filter(User.name == user_name).one()
    perm = session_add_new_room.query(Perm).filter(Perm.name == 'admin').one()
    a = Associations()
    a.user = user
    a.perm = perm
    room = Room(room_name)
    room.user.append(a)
    session_add_new_room.add(a)
    session_add_new_room.add(room)
    session_add_new_room.commit()
    room_users = {}
    answer = dict(room_name=room.name, perm=session_add_new_room.query(Perm.id, Perm.name, Perm.add_user, Perm.create_room,
                                               Perm.create_vote, Perm.delete_room, Perm.delete_user,
                                               Perm.delete_vote, Perm.make_secure, Perm.make_unsecure,
                                               Perm.voting, Perm.edit_perm, Perm.edit_perm_def).filter(
                                Perm.id == perm.id).one().__dict__, users=room_users, secure=room.secure, auth=room.auth)

    session_add_new_room.close()
    return answer


def delete_room(room_name):
    session_del_room = Session()
    room = session_del_room.query(Room).filter(Room.name == room_name).one()
    for assoc in room.user:
        session_del_room.delete(assoc)
        session_del_room.flush()
        session_del_room.commit()
    session_del_room.delete(room)
    session_del_room.commit()
    session_del_room.close()


def room_change_auth(room_name, auth):
    session_change_settings = Session()
    room = session_change_settings.query(Room).filter(Room.name == room_name).one()
    old_param = room.auth
    if old_param != auth:
        room.auth = auth
    session_change_settings.commit()
    session_change_settings.close()


def room_change_secure_settings(room_name, secure, change_pass, old_pass, new_pass):

    session_change_settings = Session()
    room = session_change_settings.query(Room).filter(Room.name == room_name).one()
    if room.secure:

        if secure and change_pass and old_pass == room.password:
            room.password = new_pass
        elif not secure and old_pass == room.password:
            room.secure = 0
            room.password = None
            answer = 'change secure'
    else:
        if secure and change_pass:
            room.secure = 1
            room.password = new_pass
            answer = 'change secure'

    session_change_settings.commit()
    return answer
    session_change_settings.close()


def check_room_password(room_name, password):
    session_check_room_pass = Session()
    room = session_check_room_pass.query(Room).filter(Room.name == room_name).one()
    if room.password == password:
        return True
    else:
        return False

    session_check_room_pass.close()







