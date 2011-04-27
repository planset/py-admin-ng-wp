#!/usr/bin/env python
# encoding: utf-8
"""
test_easylock.py

Created by planset on 2011-04-26.
Copyright (c) 2011 Daisuke Igarashi. All rights reserved.
"""

import sys
import os
from subprocess import *
from easylock import *
from nose.tools import *

LOCKFILE="/tmp/EasyLock"

def setup():
    if os.path.exists(LOCKFILE):
        call(["rm", LOCKFILE])
    
def getlines(filename):
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    return lines


def testNew():
    o = EasyLock()
    o.lock("aaaa")
    lines = getlines("lock")
    eq_("aaaa", lines[0])
    
def testNew2():
    o = EasyLock(LOCKFILE)
    o.lock("aaaa")
    lines = getlines(LOCKFILE)
    eq_("aaaa", lines[0])
    
def testLock():
    o = EasyLock(LOCKFILE)
    o.lock("aaaa")
    o.lock("bbbb")
    o.lock("cccc")
    lines = getlines(LOCKFILE)
    eq_("aaaa", lines[0])
    eq_("bbbb", lines[1])
    eq_("cccc", lines[2])

def testUnlock():
    o = EasyLock(LOCKFILE)
    o.lock("aaaa")
    o.lock("bbbb")
    o.lock("cccc")
    o.unlock("bbbb")
    lines = getlines(LOCKFILE)
    eq_("aaaa", lines[0])
    eq_("cccc", lines[1])
    
if __name__ == '__main__':
    import nose
    nose.main()

