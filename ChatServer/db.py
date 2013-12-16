#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from sqlalchemy import Column, Date, Integer, String, Table
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///C:\\sqlitedbs\\chatTest.db', echo=True)
Base = declarative_base()

association_room_user = Table('room_user', Base.metadata,
    Column('room_id', Integer, ForeignKey('room.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)

#association_room_vote = Table('room_vote', Base.metadata,
#    Column('room_id', Integer, ForeignKey('room.id')),
#    Column('vote_id', Integer, ForeignKey('vote.id'))
#)
#
#association_user_vote = Table('user_vote', Base.metadata,
#    Column('user_id', Integer, ForeignKey('user.id')),
#    Column('vote_id', Integer, ForeignKey('vote.id'))
#)

class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    auth = Column(Integer(1))
    password = Column(String(20))
    secure = Column(Integer(1))
    user = relationship("User", secondary=association_room_user, backref="room")


    def __init__(self, name):

        self.name = name

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    registered = Column(Integer(1))
    admin = Column(Integer(1))
    name = Column(String(255))
    password = Column(String(20))
    login = Column(String(70))
    perm = relationship("Perm")

    def __init__(self, name):

        self.name = name

class Perm(Base):
    __tablename__ = 'perm'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, name):

        self.name = name





Base.metadata.create_all(engine)



