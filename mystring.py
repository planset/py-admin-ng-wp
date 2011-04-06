#!/usr/bin/env python
# encoding: utf-8
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


alphabets = string.digits + string.letters

def randstr(n=64):
    return ''.join(random.choice(alphabets) for i in xrange(n))

  

def replace(file_name, from_pattern, to_pattern):
    read_file = None
    write_file = None
    temp_file = "temp_file"
    try:
        read_file = open(file_name, 'r')
        write_file = open(temp_file, 'w')
        for line in read_file:
            if line.find(from_pattern) != -1:
                line = re.sub(from_pattern, to_pattern, line)
            write_file.write(line)
    finally:
        read_file.close()
        write_file.close()

    if os.path.isfile(file_name) and os.path.isfile(temp_file):
        os.remove(file_name)
        os.rename(temp_file, file_name)

