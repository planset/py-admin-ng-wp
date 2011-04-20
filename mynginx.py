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





def _get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()


class SiteType(object):
    NORMAL, WORDPRESS, GUNICORN, SPHINX = range(4)
    words = ["normal", "wordpress", "gunicorn", "sphinx"]

class Site(object):
    def __init__(self, name, site_type):
        self.name = name
        self.__site_type = site_type
        self.status = "stop"

    def get_site_type(self):
        return SiteType.words[self.__site_type]
    def set_site_type(self, value):
        self.__site_type = value

    site_type = property(get_site_type, set_site_type)

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
    
    def __init__(self, import_name):
        self.config = Config(_get_package_path(import_name), self.default_config)
        pass
    
    def get_available_sites(self):
        """
        sites-availableにあるファイルから設定済みのサイトの一覧を取得する。
        """
        return self._get_sites(self.sites_available_dir_path)

    def get_enabled_sites(self):
        """
        sites-enabledにあるファイルから設定済みのサイトの一覧を取得する。
        """
        return self._get_sites(self.sites_enabled_dir_path)

    def _get_sites(self, target_dir):
        """
        target_dirのファイルを取得して設定済みのサイトのリストを返す。
        """
        p = Popen(["ls", target_dir], stdin=PIPE, stdout=PIPE)
        return ( Site(site, self._get_site_type(site)) for site in p.stdout.read().splitlines() )

    def _get_site_type(self, site):
        """
        サイトの格納ディレクトリを調査し、どの種別のサイトかを返す。
        """
        sub_domain, domain = split_subdomain(site)

        p = Popen(["ls", os.path.join(self.wwwroot_dir_path, domain, sub_domain)], stdin=PIPE, stdout=PIPE)
        file_list = p.stdout.read().splitlines() 
        if "wp-config.php" in file_list:
            return SiteType.WORDPRESS
        elif "gunicorn" in file_list:
            return SiteType.GUNICORN
        elif "conf.py" in file_list and "index.rst" in file_list:
            return SiteType.SPHINX
        else:
            return SiteType.NORMAL


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
        
    def add_site(self, target_domain, site_type="wordpress"):
        sub_domain, domain = split_subdomain(target_domain)

        if domain == "":
            return False

        site = get_site_manager(site_type)
        site.create(domain, sub_domain, self.config, self.get_backend_port())

        #self.start(target_domain)
        return True

    def remove_site(self, target_domain):
        if target_domain in ["www.lowlevellife.com", "ezock.com"]:
            return

        sub_domain, domain = split_subdomain(target_domain)
        site_type = self._get_site_type(target_domain)

        self.stop(target_domain)

        site = get_site_manager(SiteType.words[site_type])
        site.delete(domain, sub_domain, self.config)

        return True


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



class SiteManager(object):
    def __init__(self):
        self._site_type = ""

    def create(self, domain, sub_domain):
        pass

    def delete(self, domain, sub_domain):
        pass
        

class SiteWordpress(SiteManager):
    def __init__(self):
        super(SiteWordpress, self).__init__()
        self._site_type = SiteType.WORDPRESS

    def create(self, domain, sub_domain, config, backend_port):
        """
        create wordpress site
        #. copy wordpress files to www_root_dir/domain/sub_domain
        #.  
        """
        #super(SiteWordpress, self).create(domain, sub_domain, nginx_dir, wwwroot_dir)

        target_domain = sub_domain + "." + domain
        wwwroot_dir = config["WWWROOT_DIR_PATH"]
        target_dir = os.path.join(config["WWWROOT_DIR_PATH"], domain, sub_domain) + DS


        # copy wordpress data
        call(["cp", "-R", "/var/wordpress", wwwroot_dir + DS + domain + DS])
        call(["mv", 
                    wwwroot_dir + DS + domain + DS + "wordpress",
                    wwwroot_dir + DS + domain + DS + sub_domain])
        db_name = re.sub("\.", "_", target_domain)
        replace(target_dir + "wp-config.php" , "\$DOMAIN", db_name)
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
        nginx_dir = config["CONF_DIR_PATH"]
        conf_file = config["SITES_AVAILABLE_DIR_PATH"] + DS + target_domain
        call(["cp", nginx_dir + DS + "basewp.conf", conf_file])
        #backend_port = self.get_backend_port()
        print "!!!", conf_file, target_domain
        replace(conf_file, "\$DOMAIN", target_domain)
        replace(conf_file, "\$SUBDOMAIN", sub_domain)
        replace(conf_file, "\$BACKEND_NAME", db_name)
        replace(conf_file, "\$BACKEND_PORT", str(backend_port))
        replace(conf_file, "\$TARGET_DIR", wwwroot_dir + DS+ domain + DS + sub_domain)

    def delete(self, domain, sub_domain, config):
        target_domain = sub_domain + "." + domain
        target_dir = os.path.join(config["WWWROOT_DIR_PATH"], domain, sub_domain)
        conf_file = os.path.join(config["SITES_AVAILABLE_DIR_PATH"], target_domain)

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




