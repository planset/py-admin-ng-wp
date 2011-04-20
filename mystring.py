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

# for split_subdomain
RE_SPLIT_SUB_DOMAIN = re.compile(r"([^\.]*)\.(.*)")

# for randstr
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


def split_subdomain(domain):
    """全然正確ではないけども、ドメインとサブドメインにわける処理。というより一番最初のピリオドで二つに分ける処理
    >>> sub_domain, domain = split_subdomain("www.test.com")
    >>> print sub_domain
    www
    >>> print domain
    test.com
    
    >>> sub_domain, domain = split_subdomain("aaa.bbb.ccc.ddd.eee")
    >>> print sub_domain
    aaa
    >>> print domain
    bbb.ccc.ddd.eee
    """
    m = RE_SPLIT_SUB_DOMAIN.match(domain)
    domain = sub_domain = ""
    if m and len(m.groups()) > 1:
        sub_domain = m.groups()[0]
        domain = m.groups()[1]
    return [sub_domain, domain]


