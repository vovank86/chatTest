#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Vladimir Kanubrikov'

from sqlalchemy import  create_engine, ForeignKey
from sqlalchemy import  Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///C:\\sqlitedbs\\chatTest.db', echo=True)
Base = declarative_base()


