import os

def numCpus():
    if not hasattr(os, 'sysconf'):
        raise RuntimeError('No sysconf detected.')
    return os.sysconf('SC_NPROCESSORS_ONLN')

#bind = 'unix:/var/run/gunicorn/admin.sock'
bind = '127.0.0.1:12321'
#workers = numCpus() * 2 + 1
workers = 1
worker_class = 'egg:meinheld#gunicorn_worker'
pidfile = '/var/run/gunicorn/admin.pid'

