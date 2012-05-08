#!/usr/bin/env python
import os
folder = "/home/server/scipy-verifier/"

if __name__=="__main__":
    #cd
    os.chdir(folder)
    #git pull
    msg =  os.popen("/usr/bin/env git pull origin master").read()
    msg = msg.splitlines()
    if len(msg)>1:
        #stop
        print os.popen("/usr/bin/env python "+folder+"stop_verifiers.py").read()
        #start
        os.execl("/usr/bin/env","python",folder+"start_verifiers.py")