#!/usr/bin/env python
import os
folder = "/home/server/scipy-verifier/"

if __name__=="__main__":
    #delete old file
    os.popen("rm -rf /home/verifiers/unity/out").read()
    os.popen("rm -rf /home/verifiers/unity/build").read()
    os.popen("rm -rf /home/verifiers/unity/test").read()
    os.popen("mkdir /home/verifiers/unity/test").read()
    os.popen("mkdir /home/verifiers/unity/out").read()
    os.popen("mkdir /home/verifiers/unity/build").read()
    
    os.popen("chmod 777 -R /home/verifiers").read()
    os.popen("chown verifiers:verifiers -R /home/verifiers").read()
    """
    #cd
    os.chdir(folder)
    #git pull
    msg =  os.popen("/usr/bin/env git pull origin master").read()
    msg = msg.splitlines()
    #stop
    print os.popen("/usr/bin/env python "+folder+"stop_verifiers.py").read()
    #start
    os.execl("/usr/bin/env","python",folder+"start_verifiers.py")"""