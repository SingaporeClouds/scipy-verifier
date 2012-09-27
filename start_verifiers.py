#!/usr/bin/python
# start the server
import os,sys
folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder)
#clean ports
print "closing ports"
os.popen("fuser -k 80/tcp").read()
os.popen("fuser -k 2012/tcp").read()
#compile and run java server

#run python server
output = str(os.spawnv(os.P_NOWAIT,sys.executable,("python",folder+"/server.py","")))
_file = open("pid","w")
_file.write(output)
_file.close()
print "server opened"