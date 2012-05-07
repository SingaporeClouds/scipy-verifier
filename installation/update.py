#!/usr/bin/env python
import os
folder = "/home/server/scipy-verifier/"

if __name__=="__main__":
    #cd
    os.chdir(folder)
    #stop
    print os.popen("/usr/bin/env python "+folder+"stop.py").read()
    #git pull
    print os.popen("/usr/bin/env git pull").read()
    #start
    print os.popen("/usr/bin/env python "+folder+"start.py").read()