# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys

from subprocess import *
import re
import passwd
from mystring import *
import MySQLdb

RE_SPLIT_SUB_DOMAIN = re.compile(r"([^\.]*)\.(.*)")

NGINX_SCRIPT = "/etc/init.d/nginx"
NGINX_DIR = "/etc/nginx"
SITES_AVAILABLE_DIR = "sites-available"
SITES_ENABLED_DIR = "sites-enabled"
WWWROOT_DIR = "/var/wwwroot"
DIR_SEPARATOR = "/"

def get_sites_available(target_dir=NGINX_DIR+DIR_SEPARATOR+SITES_AVAILABLE_DIR):
    """docstring for get_domains"""
    p = Popen(["ls", target_dir], stdin=PIPE, stdout=PIPE)
    sites = p.stdout.read().splitlines()
    return sites

def get_sites_enabled(target_dir=NGINX_DIR+DIR_SEPARATOR+SITES_ENABLED_DIR):
    """"""
    p = Popen(["ls", target_dir], stdin=PIPE, stdout=PIPE)
    sites = p.stdout.read().splitlines()
    return sites

def nginx_reload():
    try:
        p = Popen([NGINX_SCRIPT, "reload"])
    except:
        pass
    
def stop(target_domain, nginx_dir=NGINX_DIR):
    p = Popen(["rm", nginx_dir + DIR_SEPARATOR + SITES_ENABLED_DIR + DIR_SEPARATOR + target_domain])
    nginx_reload()

def start(target_domain, nginx_dir=NGINX_DIR):
    p = Popen(["ln", "-s", nginx_dir + DIR_SEPARATOR + SITES_AVAILABLE_DIR + DIR_SEPARATOR + target_domain,
               nginx_dir + DIR_SEPARATOR + SITES_ENABLED_DIR + DIR_SEPARATOR])
    nginx_reload()

def get_backend_port(backend_file_path="/etc/nginx/backend_port"):
    with open(backend_file_path, "r") as f:
        line = f.readline()
    backend_port = int(line) + 1
    with open(backend_file_path, "w") as f:
        f.write(str(backend_port))
    return backend_port

def addnewsite(target_domain, nginx_dir=NGINX_DIR, wwwroot_dir=WWWROOT_DIR):
    m = RE_SPLIT_SUB_DOMAIN.match(target_domain)
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    target_dir = WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + sub_domain + DIR_SEPARATOR

    # mkdir

    # copy wordpress data
    call(["cp", "-R", "/var/wordpress", target_dir])
    call(["mv", 
                WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + "wordpress",
                WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + sub_domain])
    db_name = re.sub("\.", "_", target_domain)
    replace(target_dir + "wp-config.php" , "\$DOMAIN", db_name)
    call(["chown", "-R", "nginx:webadmin", target_dir])
    call(["find", target_dir, "-type", "d", "|xargs chmod g+w"])
    
    # add ftp user
    call(["useradd", "-d", target_dir, target_domain ])
    call(["gpasswd", "-a", target_domain, "webadmin"])
    passwd.passwd(target_domain, "password1234")
    
    # add database
    con = MySQLdb.connect(host="localhost", port=3306, user="webuser", passwd="webuser")
    cur = con.cursor()
    try:
        cur.execute("create database " + db_name + ";")
        cur.execute("GRANT ALL PRIVILEGES ON " + db_name + ".* TO 'webuser'@'localhost' IDENTIFIED BY 'webuser' WITH GRANT OPTION;")
        cur.execute("FLUSH PRIVILEGES;")
    except:
        pass
    cur.close()
    con.close()


    # nginx settings
    conf_file = nginx_dir + DIR_SEPARATOR + SITES_AVAILABLE_DIR + DIR_SEPARATOR + target_domain
    call(["cp", nginx_dir + DIR_SEPARATOR + "basewp.conf", conf_file])
    backend_port = get_backend_port()
    replace(conf_file, "\$DOMAIN", target_domain)
    replace(conf_file, "\$SUBDOMAIN", sub_domain)
    replace(conf_file, "\$BACKEND_NAME", db_name)
    replace(conf_file, "\$BACKEND_PORT", str(backend_port))
    replace(conf_file, "\$TARGET_DIR", WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + sub_domain)

    #start(target_domain, nginx_dir)


def delete(target_domain, nginx_dir=NGINX_DIR, wwwroot_dir=WWWROOT_DIR):
    if target_domain in ["www.lowlevellife.com", "ezock.com", "admin.ezock.com"]:
        return

    m = RE_SPLIT_SUB_DOMAIN.match(target_domain)
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    target_dir = WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + sub_domain 
    conf_file = nginx_dir + DIR_SEPARATOR + SITES_AVAILABLE_DIR + DIR_SEPARATOR + target_domain

    stop(target_domain, nginx_dir)

    call(["rm", "-Rf", target_dir])
    call(["rm", conf_file])
    call(["userdel", target_domain])

    db_name = re.sub("\.", "_", target_domain)
    con = MySQLdb.connect(host="localhost", port=3306, user="webuser", passwd="webuser")
    cur = con.cursor()
    try:
        cur.execute("drop database " + db_name + ";")
        cur.execute("REVOKE ALL PRIVILEGES ON " + db_name + ".* FROM 'webuser'@'localhost';")
        cur.execute("FLUSH PRIVILEGES;")
    except:
        pass
    cur.close()
    con.close()




