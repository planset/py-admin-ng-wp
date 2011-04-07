#!/usr/bin/env python
# encoding: utf-8
from __future__ import with_statement
"""
libstring.py

Created by planset on 2011-03-31.
Copyright (c) 2011 Daisuke Igarashi. All rights reserved.
"""


import string
import random
import re
import sys
import os
import codecs


alphabets = string.digits + string.letters

def randstr(n=64):
    return ''.join(random.choice(alphabets) for i in xrange(n))


def replace(file_name, from_pattern, to_pattern, enc="utf-8"):
    with codecs.open(file_name, "r", encoding=enc) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        new_lines.append(re.sub(from_pattern, to_pattern, line))

    with codecs.open(file_name, "w", encoding=enc) as f:
        for line in new_lines:
            f.write(line)

