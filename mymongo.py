#!/usr/bin/env python
# encoding: utf-8
"""
db.py

Created by planset on 2011-03-31.
Copyright (c) 2011 Daisuke Igarashi. All rights reserved.
"""

import myjp
import datetime
from pymongo import Connection

MONGO_DB_SERVER = "localhost"
DATABASE_NAME = "py-admin-ng-wp"
ADMIN_PASSWORD = "password"


def connect_db():
    try:
        connection = Connection(MONGO_DB_SERVER)
        return connection[DATABASE_NAME]
    except:
        return None

def exist_admin_user(db):
    if db.users.find_one({"user_login":"admin"}):
        return True
    return False
    
def init_db(db, user_password, app=None):
    if db.users.find_one({"user_login":"admin"}) is None:
        if app:
            app.logger.debug("add admin user")
        db.users.insert({"user_login":"admin"
                       , "user_password":user_password
                       , "user_display_name":u"管理者"
                       , "user_emal":""
                       , "user_url":""
                       , "user_registered":myjp.utc_from_jst(datetime.datetime.now())
                       , "user_level":0
                       , "user_status":0
                       })
        return True
    return False