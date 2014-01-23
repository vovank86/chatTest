#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from sqlalchemy import Column, Date, Integer, String, Table
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship, backref, session, query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from getpass import *
import hashlib

engine = create_engine('sqlite:///C:\\sqlitedbs\\chatTest.db', echo=True)
Base = declarative_base()

#association_room_user_perm = Table('room_user_perm', Base.metadata,
#                                   Column('room_id', Integer, ForeignKey('room.id')),
#                                   Column('user_id', Integer, ForeignKey('user.id')),
#                                   Column('perm_id', Integer, ForeignKey('perm.id'))
#)

class Associations(Base):
    __tablename__ = 'associations'

    room_id = Column(Integer, ForeignKey('room.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    perm_id = Column(Integer, ForeignKey('perm.id'))
    perm = relationship("Perm")
    user = relationship("User")


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    auth = Column(Integer(1))
    password = Column(String(20))
    secure = Column(Integer(1))
    user = relationship("Associations")
    vote = relationship("Vote")

    def __init__(self, name):
        self.name = name
        self.auth = 0
        self.secure = 0


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    registered = Column(Integer(1))
    name = Column(String(255))
    password = Column(String(20))
    login = Column(String(70))
    vote = relationship("Vote")

    def __init__(self, login, name, password, registered):
        self.login = login
        self.name = name
        self.password = password
        self.registered = registered


class Perm(Base):
    __tablename__ = 'perm'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    create_room = Column(Integer(1))
    delete_room = Column(Integer(1))
    create_vote = Column(Integer(1))
    delete_vote = Column(Integer(1))
    voting = Column(Integer(1))
    make_secure = Column(Integer(1))
    make_unsecure = Column(Integer(1))
    add_user = Column(Integer(1))
    delete_user = Column(Integer(1))

    def __init__(self, name, create_room, delete_room, create_vote, delete_vote, voting, make_secure, make_unsecure,
                 add_user,
                 delete_user):
        self.name = name
        self.create_room = create_room
        self.delete_room = delete_room
        self.create_vote = create_vote
        self.delete_vote = delete_vote
        self.voting = voting
        self.make_secure = make_secure
        self.make_unsecure = make_unsecure
        self.add_user = add_user
        self.delete_user = delete_user


class Vote(Base):
    __tablename__ = 'vote'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    summary_vote = Column(Integer)

    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id
        self.summary_vote = 1

    def __add_vote__(self):
        self.summary_vote += 1


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


def install_chat(session):
    """
    This is a procedure for first setup chat application.
    It use the command line for setup first user - root user, whom will has fool permissions.

    """
    print "It's first run of the CHAT SERVER.\nSo you need to answer few questions..."
    login = raw_input('Please type the nick-name (Login) of the root user: ')
    name = raw_input('\nPlease type your fool name (Screen Name):')
    password = make_server_password()


    root_perm = Perm("root", 1, 1, 1, 1, 1, 1, 1, 1, 1)
    admin_perm = Perm("admin", 1, 0, 1, 1, 1, 1, 1, 1, 1)
    authorised_perm = Perm("auth_user", 1, 0, 1, 0, 1, 0, 0, 0, 0)
    guest_perm = Perm("guest", 0, 0, 1, 0, 1, 0, 0, 0, 0)

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
    print '\nNow the server is starting...'


def auth_user(login, password):
    """
    @rtype : object
    """
    session = Session()
    for instance in session.query(User).order_by(User.id):
        if login == instance.login:
            user = instance
            if not check_pass(user, password):
                return False
            else:
                return start_sys(user)
        else:
            return False

    session.commit()
    session.close()


def check_pass(user, password):
    if password == user.password:
        return user
    else:
        return False


def registration(login, name, password):
    session_reg = Session()
    user = session_reg.query(User).filter(User.login.in_([login])).one()
    user.password = hashlib.md5(password).hexdigest()
    auth_perm = session.query(Perm).filter(Perm.name.in_(['auth_user']))
    room = session_reg.query(Room).filter(Room.name.in_(['default_room']))
    a = session_reg.query(Associations).filter(Associations.user_id == user.id and Associations.room_id == room.id)
    a.perm = auth_perm
    session.commit()
    session.close()
    start_sys(user)


def start_sys(user):
    """
    This function return data for UI initialisation.
    @param user
    """


    return user