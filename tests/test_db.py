# coding: utf-8
"""
test for db
"""

from nose.tools import ok_, eq_

import db
from flask import g

def test_setup_db():
    ok_(db.setup_db())
    ok_(g.db is not None)
    


