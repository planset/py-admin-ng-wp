# coding: utf-8

import settings
from flask import Flask
from flask import (
    g, redirect, url_for, session, request, make_response,
    render_template, abort, flash, get_flashed_messages,
)
from decorators import login_required, admin_required
import myjp

import mynginx

from mymongo import connect_db, init_db, exist_admin_user
from mystring import randstr

app = Flask(__name__)
app.config.from_object('settings')


@app.before_request
def before_request():
    """
    if the session includes a user_key it will also try to fetch
    the user's object from memcache (or the datastore).
    if this succeeds, the user object is also added to g.
    """
    g.db = connect_db() or abort(500)
    
    if 'user_login' in session:
        try:
            g.user = g.db.users.find_one({"user_login":session['user_login']})
            session["user_display_name"] = g.user["user_display_name"]
            session["logged_in"] = True
        except :
            g.user = None
    else:
        g.user = None
        
        
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = randstr()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.after_request
def after_request(response):
    return response

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404

@app.errorhandler(500)
def page_not_found(error):
    return render_template("internal_server_error.html"), 500





@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/')
@login_required
def index():
    return list()
    
@app.route("/list")
@login_required
def list():
    asites = mynginx.get_sites_available(settings.NGINX_DIR + "/" + settings.SITES_AVAILABLE_DIR)
    esites = mynginx.get_sites_enabled(settings.NGINX_DIR + "/" + settings.SITES_ENABLED_DIR)
    
    sites = []
    app.logger.debug(asites)
    app.logger.debug(esites)
    for asite in asites:
        if asite in esites:
            sites.append({"domain":asite, "status":"running"})
        else:
            sites.append({"domain":asite, "status":"stop"})
    
    app.logger.debug(sites)
    return render_template("list.html", sites=sites)

@app.route("/addnewsite", methods=['POST', 'GET'])
@login_required
def addnewsite():
    if request.method=="POST" and reuest.form.get("domain_name"):
        mynginx.addnewsite(reuest.form.get("domain_name"))
        flash("add new site")
        return redirect(url_for("list"))
    else:
        return render_template("addnewsite.html")

@app.route("/action", methods=["POST", "GET"])
@login_required
def action():
    if request.method=="POST" and request.form.get("action"):
        action = request.form.get("action")
        domain_name = request.form.get("domain_name")
        app.logger.debug("action="+action+"   domain_name="+domain_name)
        if action == "start":
            start(domain_name)
        elif action == "stop":
            stop(domain_name)
        elif action == "delete":
            delete(domain_name)
        else:
            flash("parameter error")

    return redirect(url_for("list"))
    
def start(domain_name):
    if domain_name:
        mynginx.start(domain_name, nginx_dir=settings.NGINX_DIR)
        flash("start")
    
def stop(domain_name):
    if domain_name:
        mynginx.stop(domain_name, nginx_dir=settings.NGINX_DIR)
        flash("stop")

def delete(domain_name):
    if domain_name:
        mynginx.delete(domain_name, nginx_dir=settings.NGINX_DIR)
        flash("delete")

@app.route("/admin")
@login_required
def admin():
    return render_html("admin.html")




@app.route("/setup", methods=['POST', 'GET'])
def setup():
    if request.method == "POST":
        init_db(g.db, request.form.get("user_password"), app)
        return render_template("setup_result.html", result="registerd!")
    else:
        if exist_admin_user(g.db):
            abort(404)
        else:
            return render_template("setup.html")
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if g.user:
        return redirect(url_for("index"))

    user_login = user_password = ""

    if request.method == 'POST':
        user_login = request.form['user_login']
        user_password = request.form['user_password']
        if valid_login(user_login, user_password):
            session["user_login"] = user_login

            next_url = request.form.get('next') or "/"

            response = make_response(redirect(next_url))

            if request.form.has_key('save_user_login_and_password'):
                response.set_cookie('user_login', user_login)
                response.set_cookie('user_password', user_password)
            else:
                response.set_cookie('user_login', expires=1)
                response.set_cookie('user_password', expires=1)

            flash("You were logged in")
            return response
        else:
            flash('Invalid username/password')

    next = request.args.get("next") or request.form.get("next") or "/"
    user_login = get_cookie("user_login")
    user_password = get_cookie("user_password")
    if len(user_login) > 0 or len(user_password) > 0:
        save_user_login_and_password = "Checked"
    return render_template("login.html", **locals())

def valid_login(user_login, user_password):
    user = g.db.users.find_one({"user_login":user_login})
    if user:
        if user_password == user["user_password"]:
            return True
    return False

def get_cookie(key):
    if request.cookies.has_key(key):
        return request.cookies.get(key)
    else:
        return ""

@app.route("/logout")
def logout():
    do_logout()
    return redirect(url_for("index"))

def do_logout():
    g.user = None
    session.pop('user_login', None)
    session.pop('user_display_name', None)
    session.pop('logged_in', None)
    flash("You were logged out")



if __name__ == '__main__':
    app.run(debug=True)