# coding: UTF-8

from flask import (g, request, redirect, url_for)

from functools import wraps

def admin_required(f):
    """
    管理者権限がない場合、エラーとする処理
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        user = g.db.users.find_one({"user_login":g.user})
        if user["user_level"] > 0:
            abort(401)
        return decorated_function
        

def login_required(f):
    """
    redirects to the index page if the user has no session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



