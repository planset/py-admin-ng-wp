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
DS = "/"


def get_site_manager(self, site_type):
    """
        get SiteManager instance
    """
    if site_type == "normal":
        return SiteNormal()
    elif site_type == "gunicorn":
        return SiteGunicorn()
    elif site_type == "shpinx":
        return SiteSphinx()
    elif site_type == "wordpress":
        return SiteWordpress()
    else:
        return None


class SiteManager:
    def __init__(self):
        self._site_type = ""
    def create(self, domain, sub_domain, nginx_dir, wwwroot_dir):
        pass
    def delete(self, domain, sub_domain, nginx_dir, wwwroot_dir):
        pass

class SiteWordpress(SiteManager):
    def __init__(self):
        self._site_type = "wordpress"

    def create(self, domain, sub_domain, nginx_dir, wwwroot_dir):
        """
        create wordpress site
        #. copy wordpress files to www_root_dir/domain/sub_domain
        #.  
        """
        super(SiteWordpress, self).create(domain, sub_domain, nginx_dir, wwwroot_dir)

        target_domain = sub_domain + "." + domain
        target_dir = wwwroot_dir + DS + domain + DS + sub_domain + DS

        # copy wordpress data
        call(["cp", "-R", "/var/wordpress", self._target_dir])
        call(["mv", 
                    wwwroot_dir + DS + domain + DS + "wordpress",
                    wwwroot_dir + DS + domain + DS + sub_domain])
        db_name = re.sub("\.", "_", target_domain)
        replace(self._target_dir + "wp-config.php" , "\$DOMAIN", db_name)
        call(["chown", "-R", "nginx:webadmin", target_dir])
        call(["find", target_dir, "-type", "d", "|xargs chmod g+w"])
        
        ## add ftp user
        #call(["useradd", "-d", target_dir, target_domain ])
        #call(["gpasswd", "-a", target_domain, "webadmin"])
        #passwd.passwd(target_domain, "password1234")
        
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
        conf_file = nginx_dir + DS + SITES_AVAILABLE_DIR + DS + target_domain
        call(["cp", nginx_dir + DS + "basewp.conf", conf_file])
        backend_port = get_backend_port()
        replace(conf_file, "\$DOMAIN", target_domain)
        replace(conf_file, "\$SUBDOMAIN", sub_domain)
        replace(conf_file, "\$BACKEND_NAME", db_name)
        replace(conf_file, "\$BACKEND_PORT", str(backend_port))
        replace(conf_file, "\$TARGET_DIR", WWWROOT_DIR + DS + domain + DS + sub_domain)

    def delete_wordpress_site(domain, sub_domain, nginx_dir, wwwroot_dir):
        target_domain = sub_domain + "." + domain
        target_dir = wwwroot_dir+ DS + domain + DS + sub_domain 
        conf_file = nginx_dir + DS + SITES_AVAILABLE_DIR + DS + target_domain


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

def SiteGunicorn(SiteManager):
    pass
def SiteNormal(SiteManager):
    pass
def SiteSphinx(SiteManager):
    pass


class Site:
    def __init__(self, name, site_type):
        self.name = name
        self.site_type = site_type
        self.status = "stop"

def get_sites_available(target_dir=NGINX_DIR+DS+SITES_AVAILABLE_DIR):
    """docstring for get_domains"""
    return get_sites(target_dir)

def get_sites_enabled(target_dir=NGINX_DIR+DS+SITES_ENABLED_DIR):
    """"""
    return get_sites(target_dir)

def get_sites(target_dir):
    p = Popen(["ls", target_dir], stdin=PIPE, stdout=PIPE)
    sites = ( Site(site, get_site_type(site, WWWROOT_DIR)) for site in p.stdout.read().splitlines() )
    return sites

def get_site_type(site, target_dir):
    m = RE_SPLIT_SUB_DOMAIN.match(site)
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    p = Popen(["ls", target_dir + DS + domain + DS + sub_domain], stdin=PIPE, stdout=PIPE)
    file_list = p.stdout.read().splitlines() 
    if "wp-config.php" in file_list:
        return "wordpress"
    elif "gunicorn" in file_list:
        return "gunicorn"
    elif "conf.py" in file_list and "index.rst" in file_list:
        return "sphinx"
    else:
        return "normal"


def nginx_reload():
    try:
        p = Popen([NGINX_SCRIPT, "reload"])
    except:
        pass
    
def stop(target_domain, nginx_dir=NGINX_DIR):
    p = Popen(["rm", nginx_dir + DS + SITES_ENABLED_DIR + DS + target_domain])
    nginx_reload()

def start(target_domain, nginx_dir=NGINX_DIR):
    p = Popen(["ln", "-s", nginx_dir + DS + SITES_AVAILABLE_DIR + DS + target_domain,
               nginx_dir + DS + SITES_ENABLED_DIR + DS])
    nginx_reload()

def get_backend_port(backend_file_path="/etc/nginx/backend_port"):
    with open(backend_file_path, "r") as f:
        line = f.readline()
    backend_port = int(line) + 1
    with open(backend_file_path, "w") as f:
        f.write(str(backend_port))
    return backend_port

def addnewsite(target_domain, site_type="wordpress", nginx_dir=NGINX_DIR, wwwroot_dir=WWWROOT_DIR):
    m = RE_SPLIT_SUB_DOMAIN.match(target_domain)
    domain = sub_domain = ""
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    if domain == "":
        return False

    site = get_site_manager(site_type)
    site.create(domain, sub_domain, nginx_dir=nginx_dir, wwwroot_dir=wwwroot_dir)

    #start(target_domain, nginx_dir)
    return True


def delete(target_domain, site_type="wordpress", nginx_dir=NGINX_DIR, wwwroot_dir=WWWROOT_DIR):
    if target_domain in ["www.lowlevellife.com", "ezock.com"]:
        return

    m = RE_SPLIT_SUB_DOMAIN.match(target_domain)
    if m:
        sub_domain = m.group(1)
        domain = m.group(2)

    stop(target_domain, nginx_dir)

    site = get_site_manager(site_type)
    site.delete(domain, sub_domain, nginx_dir=nginx_dir, wwwroot_dir=wwwroot_dir)



