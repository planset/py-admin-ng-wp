# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys

import os
from subprocess import *
import re
import passwd
from mystring import *
import MySQLdb

from flask.config import *


class WebServerTypeError(Exception):
    pass

class WebServerType(object):
    NGINX, APACHE, LIGHTTPD = range(3)
    words = ["nginx", "apache", "lighttpd"]

def get_wsc(site_type):
    if site_type == WebServerType.NGINX:
        return NginxController()
    elif site_type == WebServerType.APACHE:
        return ApacheController()
    elif site_type == WebServerType.LIGHTTPD:
        return LighttpdController()
    else:
        raise WebServerTypeError


class SiteType(object):
    NORMAL, WORDPRESS, GUNICORN, SPHINX = range(4)
    words = ["normal", "wordpress", "gunicorn", "sphinx"]

class SiteStatus(object):
    STOP, RUNNING = range(2)
    words = ["stop", "running"]

class Site(object):
    """
    :param: server_name: site's name = server_name
    :param: config: config
    """
    def __init__(self, server_name, wsc):
        self.name = self.server_name = server_name
        self.wsc = wsc
        self.config = wsc.config
        self.site_type = self._get_site_type(server_name)
        self.status = SiteStatus.STOP

    def _get_site_type(self, server_name):
        """
        サイトの格納ディレクトリを調査し、どの種別のサイトかを返す。
        """
        sub_domain, domain = split_subdomain(server_name)

        p = Popen(["ls", os.path.join(self.config["WWWROOT_DIR_PATH"], domain, sub_domain)], stdin=PIPE, stdout=PIPE)
        file_list = p.stdout.read().splitlines() 
        if "wp-config.php" in file_list:
            return SiteType.WORDPRESS
        elif "gunicorn" in file_list:
            return SiteType.GUNICORN
        elif "conf.py" in file_list and "index.rst" in file_list:
            return SiteType.SPHINX
        else:
            return SiteType.NORMAL

    def get_site_type_name(self):
        return SiteType.words[self.site_type]
    site_type_name = property(get_site_type_name)

    def start(self):
        self.wsc.start(self.server_name)

    def stop(self):
        self.wsc.stop(self.server_name)


class WebServerController(object):
    pass

class NginxController(WebServerController):
    """
    nginxをちょいちょいコントロールするクラス
    """
    
    conf_dir_path = ConfigAttribute("CONF_DIR_PATH")
    sites_available_dir_name = ConfigAttribute("SITES_AVAILABLE_DIR_NAME")
    sites_enabled_dir_name = ConfigAttribute("SITES_ENABLED_DIR_NAME")
    sites_available_dir_path = ConfigAttribute("SITES_AVAILABLE_DIR_PATH")
    sites_enabled_dir_path = ConfigAttribute("SITES_ENABLED_DIR_PATH")
    wwwroot_dir_path = ConfigAttribute("WWWROOT_DIR_PATH")
    backend_file_path = ConfigAttribute("BACKEND_FILE_PATH")
    
    #: Default configuration parameters.
    default_config = {
        'CONF_DIR_PATH':                    "/etc/nginx",
        'SITES_AVAILABLE_DIR_NAME':         "sites-available",
        'SITES_ENABLED_DIR_NAME':           "sites-enabled",
        'SITES_AVAILABLE_DIR_PATH':         "/etc/nginx/sites-available",
        'SITES_ENABLED_DIR_PATH':           "/etc/nginx/sites-enabled",
        'WWWROOT_DIR_PATH':                 "/var/wwwroot",
        'BACKEND_FILE_PATH':                "/etc/nginx/backend_port"
    }
    
    def __init__(self):
        self.config = Config('', self.default_config)
        pass
    
    def reload(self):
        """
        nginxの設定ファイルを再読込する。
        """
        try:
            p = Popen(["service", "nginx", "reload"])
        except:
            pass

    def stop(self, server_name):
        """
        稼働中の指定のサイトを停止させる。
        """
        p = Popen(["rm", os.path.join(self.sites_enabled_dir_path,server_name)])
        self.reload()

    def start(self, server_name):
        """
        停止中の指定のサイトを開始する。
        """
        p = Popen(["ln", "-s", os.path.join(self.sites_available_dir_path, server_name),
                   os.path.join(self.sites_enabled_dir_path, server_name)
                   ])
        self.reload()

    def get_backend_port(self):
        """
        fcgiやgunicornのバックエンドポートが重複しないようにファイルで番号を管理する。
        """
        with open(self.backend_file_path, "r") as f:
            line = f.readline()
        backend_port = int(line) + 1
        with open(self.backend_file_path, "w") as f:
            f.write(str(backend_port))
        return backend_port
        
def get_site_manager(site_type):
    """
        get SiteManager instance
    """
    if site_type == "normal":
        return SiteNormal()
    elif site_type == "gunicorn":
        return SiteGunicorn()
    elif site_type == "sphinx":
        return SiteSphinx()
    elif site_type == "wordpress":
        return SiteWordpress()
    else:
        return None

def get_site_manager_from_server_name(server_name, wsc):
    site = Site(server_name, wsc)
    return get_site_manager(site.site_type_name)

class SiteManager(object):
    def __init__(self, ws_type=WebServerType.NGINX):
        self._site_type = ""
        self.wsc = get_wsc(ws_type) 
        self.config = self.wsc.config
        self.task_up = []
        self.task_down = []

    def _set_task(self, up, down):
        self.task_up.append(up)
        self.task_down.append(down)

    def _before_api(self, server_name):
        self.sub_domain, self.domain = split_subdomain(server_name)
        self.target_domain = self.sub_domain + "." + self.domain
        self.wwwroot_dir = self.wsc.config["WWWROOT_DIR_PATH"]
        self.target_dir = os.path.join(self.wsc.config["WWWROOT_DIR_PATH"], self.domain, self.sub_domain) + DS
        self.db_name = re.sub("\.", "_", self.target_domain)
        self.nginx_dir = self.wsc.config["CONF_DIR_PATH"]
        self.conf_file = self.wsc.config["SITES_AVAILABLE_DIR_PATH"] + DS + self.target_domain

    def get_available_sites(self):
        """
        sites-availableにあるファイルから設定済みのサイトの一覧を取得する。
        """
        return self._get_sites(self.config["SITES_AVAILABLE_DIR_PATH"])

    def get_enabled_sites(self):
        """
        sites-enabledにあるファイルから設定済みのサイトの一覧を取得する。
        """
        return self._get_sites(self.config["SITES_ENABLED_DIR_PATH"])

    def _get_sites(self, target_dir):
        """
        target_dirのファイルを取得して設定済みのサイトのリストを返す。
        """
        p = Popen(["ls", target_dir], stdin=PIPE, stdout=PIPE)
        return ( Site(site, self.wsc) for site in p.stdout.read().splitlines() )

    def get_site(self, server_name):
        return Site(server_name, self.wsc)

    def create(self, server_name):
        self._before_api(server_name)
        for task in self.task_up:
            task()
        return True

    def delete(self, server_name):
        self._before_api(server_name)
        if server_name in ["www.lowlevellife.com", "ezock.com"]:
            return True
        for task in reversed(self.task_down):
            task()
        return True


class SiteWordpress(SiteManager):
    def __init__(self):
        super(SiteWordpress, self).__init__()
        self._site_type = SiteType.WORDPRESS
        self.setup()

    def setup(self):
        self._set_task(self.copy_wp_files, self.delete_wp_files)
        self._set_task(self.create_db, self.delete_db)
        self._set_task(self.create_webserver_settings, self.delete_webserver_settings)

    def copy_wp_files(self):
        call(["cp", "-R", "/var/wordpress", self.wwwroot_dir + DS + self.domain + DS])
        call(["mv", 
                    self.wwwroot_dir + DS + self.domain + DS + "wordpress",
                    self.wwwroot_dir + DS + self.domain + DS + self.sub_domain])
        replace(self.target_dir + "wp-config.php" , "\$DOMAIN", self.db_name)
        call(["chown", "-R", "nginx:webadmin", self.target_dir])
        call(["find", self.target_dir, "-type", "d", "|xargs chmod g+w"])

    def create_db(self):
        con = MySQLdb.connect(host="localhost", port=3306, user="webuser", passwd="webuser")
        cur = con.cursor()
        try:
            cur.execute("create database " + self.db_name + ";")
            cur.execute("GRANT ALL PRIVILEGES ON " + self.db_name + ".* TO 'webuser'@'localhost' IDENTIFIED BY 'webuser' WITH GRANT OPTION;")
            cur.execute("FLUSH PRIVILEGES;")
        except:
            pass
        cur.close()
        con.close()

    def create_webserver_settings(self):
        # nginx settings
        call(["cp", self.nginx_dir + DS + "basewp.conf", self.conf_file])
        backend_port = self.wsc.get_backend_port()
        replace(self.conf_file, "\$DOMAIN", self.target_domain)
        replace(self.conf_file, "\$SUBDOMAIN", self.sub_domain)
        replace(self.conf_file, "\$BACKEND_NAME", self.db_name)
        replace(self.conf_file, "\$BACKEND_PORT", str(backend_port))
        replace(self.conf_file, "\$TARGET_DIR", self.wwwroot_dir + DS+ self.domain + DS + self.sub_domain)
    def delete_wp_files(self):
        call(["rm", "-Rf", self.target_dir])

    def delete_webserver_settings(self):
        call(["rm", self.conf_file])

    def delete_db(self):
        con = MySQLdb.connect(host="localhost", port=3306, user="webuser", passwd="webuser")
        cur = con.cursor()
        try:
            cur.execute("drop database " + self.db_name + ";")
            cur.execute("REVOKE ALL PRIVILEGES ON " + self.db_name + ".* FROM 'webuser'@'localhost';")
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




