# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import sys

class EasyLock(object):
    DEFAULT_LOCK_FILE = "lock"

    def __init__(self, lockfile = DEFAULT_LOCK_FILE):
        self.lockfile = lockfile

    def is_lock(self, key):
        if os.path.exists(self.lockfile):
            with open(self.lockfile)as f:
                lines = f.read().splitlines()
            if key in lines:
                return True
        return False 

    def lock(self, key):
        has_same = False
        lines=[]
        if os.path.exists(self.lockfile):
            with open(self.lockfile, "r") as f:
                rlines = f.read().splitlines()
            for line in rlines:
                lines.append(line)
                if line == key:
                    has_same = True 
        if not has_same:
            lines.append(key)
        with open(self.lockfile, "w") as f:
            for line in lines:
                f.write(line + "\n")

    def unlock(self, key):
        if not os.path.exists(self.lockfile):
            return
        lines=[]
        with open(self.lockfile, "r") as f:
            rlines = f.read().splitlines()
        for line in rlines:
            if line != key:
                lines.append(line)

        with open(self.lockfile, "w") as f:
            for line in lines:
                f.write(line + "\n")


if __name__ == "__main__":
    from subprocess import *
    call(["rm", "lock"])

    lock = EasyLock("lock")
    lock.lock("aaaa")
    lock.lock("bbbb")
    lock.lock("cccc")
    lock.unlock("bbbb")
    with open("lock", "r")as f:
        lines = f.read().splitlines()
    if lines[0] == "aaaa":
        print "ok"
    if lines[1] == "cccc":
        print "ok"
    if lock.is_lock("aaaa"):
        print "ok"
    if not lock.is_lock("bbbb"):
        print "ok"



