#!/usr/bin/env python
# encoding: utf-8
"""
db.py

Created by planset on 2011-03-31.
Copyright (c) 2011 Daisuke Igarashi. All rights reserved.
"""
from __future__ import with_statement

import myjp
import datetime
import sqlite3

DATABASE_NAME = "my.db"

from contextlib import closing

def init_db(app):
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
def connect_db():
    try:
        return sqlite3.connect(DATABASE_NAME)
    except:
        return None

def close_db(db):
    db.close()
    
def query_db(db, query, args=(), one=False):
    try:
        cur = db.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv
    except:
        return None
    
def get_user(db, user_login, app=None):
    return query_db(db, "select * from users where user_login = ?", [user_login], one=True)
    
def get_admin_user(db):
    return get_user(db, "admin")
    
def exist_admin_user(db):
    if query_db(db, "select * from users where user_login = ?", "admin"):
        return True
    return False
    
def add_admin_user(db, user_password, app=None):
    if query_db(db, "select * from users where user_login = ?", "admin") is None:
        if app:
            app.logger.debug("add admin user")
        db.execute("insert into users(user_login, user_password, user_display_name, user_level) values (?, ?, ?, ?)", ["admin", user_password, "admin", 0])
        db.commit()
        return True
    return False