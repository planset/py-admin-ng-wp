#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from subprocess import *

def passwd(username, password):
    pipe = Popen(["passwd", username], stdin=PIPE).stdin
    if pipe:
        pipe.write(password + "\n")
        pipe.write(password + "\n")
        pipe.write("\n")
        pipe.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: # python %s user_name password" % (sys.argv[0])
        quit()

    passwd(sys.argv[1], sys.argv[2])
