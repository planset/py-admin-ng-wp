#!/usr/bin/env python
# encoding: utf-8
"""
libstring.py

Created by planset on 2011-03-31.
Copyright (c) 2011 Daisuke Igarashi. All rights reserved.
"""


import string
import random

alphabets = string.digits + string.letters

def randstr(n=64):
    return ''.join(random.choice(alphabets) for i in xrange(n))

