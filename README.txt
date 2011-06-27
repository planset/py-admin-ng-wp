test

=======================
setup development
=======================

mkvirtualenv flask_mongo
workon flask_mongo
pip install flask
#pip install pymongo
#pip install nose
#pip install coverage
#pip install unittest-xml-reporting
#pip install simplejson
#pip install uamobile
deactivate
workon flask_mongo


=======================
test
=======================
nosetests
nosetests -v
# with debug
nosetests -s --pdb 

# you want to view coverage
nosetests -v --with-coverage
coverage html
 -> html are created to "htmlcov" directory

# ref: jenkins cobertura plugin
nosetests -v -w tests/ --with-coverrage --with-xunit
coverage xml


=======================
deploy production
=======================
# setup python(on centos5.5)
wget http://www.python.org/ftp/python/2.7.1/Python-2.7.1.tar.bz2
tar jxf Python-2.7.1.tar.bz2
./conifgure CFLAGS=-fPIC --enable-shared --prefix=/usr/local
vi Modules/Setup
以下をコメントをはずす
zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz
make
make install

# 
# python -V
Python 2.7.1

# setup setup_tools
wget http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py

# setup gunicorn
easy_install gunicorn
easy_install meinheld



# setup init script
# sudo vi /etc/init.d/flasktest

	#!/bin/bash
	cd DIRECTORY
	gunicorn -c conf/gunicorn.conf.py

# chmod 755 /etc/init.d/flasktest
# chkconfig 






=======================
db
=======================

This package provides a few mappers to store feed entries
in a SQL database.

The SQL uri is provided in the config module::

    >>> import settings
    >>> import db
	>>> setup_db()


