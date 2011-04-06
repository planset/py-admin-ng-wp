# -*- coding: utf-8 -*-

from subprocess import *
import re
import passwd
from mystring import *

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

def addnewsite(target_domain, nginx_dir=NGINX_DIR, wwwroot_dir=WWWROOT_DIR):
    m = RE_SPLIT_SUB_DOMAIN.match(target_domain)
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    target_dir = WWWROOT_DIR + DIR_SEPARATOR + domain + DIR_SEPARATOR + sub_domain + DIR_SEPARATOR

    # mkdir
    check_call(["mkdir", "-p", target_dir])

    # copy wordpress data
    check_call(["cp", "-R", "/var/wordpress/*", target_dir])
    
    # change owner
    #check_call(["chown", "-R", "nginx:webadmin", target_dir])
    #check_call(["find", target_dir, "-type", "d", "|xargs chmod g+w"])
    
    # add ftp user
    check_call(["useradd", "-d", target_dir, target_domain ])
    check_call(["gpasswd", "-a", target_domain, "webadmin"])
    passwd.passwd(target_domain, "password1234")
    
    # nginx settings
    conf_file = nginx_dir + DIR_SEPARATOR + "base.conf", nginx_dir + DIR_SEPARATOR + SITES_AVAILABLE_DIR + DIR_SEPARATOR + target_domain
    check_call(["cp", nginx_dir + DIR_SEPARATOR + "base.conf", conf_file])
    replace(file, "$DOMAIN", target_domain)
    replace(file, "$SUBDOMAIN", sub_domain)
    #start(target_domain, nginx_dir)
    
    
