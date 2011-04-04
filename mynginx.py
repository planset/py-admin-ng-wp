# -*- coding: utf-8 -*-

from subprocess import *
import re

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

    # copy wordpress data
    
    # add ftp user
    
    # nginx settings
    check_call(["touch", nginx_dir + DIR_SEPARATOR + SITES_AVAILABLE_DIR + target_domain])
    start(target_domain, nginx_dir)
    
    