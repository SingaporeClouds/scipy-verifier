#!/usr/bin/env python
#stop the server

import os
folder = "/home/server/scipy-verifier/"
os.chdir(folder)

import signal

_file = open("pid","r")
pid = int(_file.read().strip())
_file.close()

try:
    os.kill(pid,signal.SIGKILL)
except:
    pass

os.popen("fuser -k 80/tcp").read()

print " Server closed"
