#!/usr/bin/python
# start the server
import os,sys
folder = os.path.dirname(__file__)
os.chdir(folder)
os.popen("fuser -k 80/tcp").read()
output = str(os.spawnv(os.P_NOWAIT,sys.executable,("python",folder+"/server.py","")))
_file = open("pid","w")
_file.write(output)
_file.close()
print "server opened"