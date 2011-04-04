import os

DEBUG = False #os.environ.get('SERVER_SOFTWARE', 'Dev').startswith('Dev')
SECRET_KEY = 'j;wD=R#2]07l65r+J)9,%)D[f:1,VS.+RQ+5VY.]lP]\wY:K'

NGINX_DIR = "/Users/planset/tmp/nginx"      #"/etc/nginx"
SITES_AVAILABLE_DIR = "sites-available"
SITES_ENABLED_DIR = "sites-enabled"
WWWROOT_DIR = "/Users/planset/tmp/wwwroot"   #"/var/wwwroot"


# CSRF_ENABLED=True
# CSRF_SESSION_LKEY=''
