#!/usr/bin/env python
import os
folder = "/home/server/scipy-verifier/"
import sys

log = open(folder+"update.log","a")
sys.stderr = log
sys.stdout = log

if __name__=="__main__":
    #delete old file
    os.popen("rm -rf /home/verifiers/unity").read()
    os.popen("rm -rf /home/verifiers/junit").read()
    
    #cd
    
    os.chdir(folder)
    
    #git pull
    msg =  os.popen("/usr/bin/env git reset --hard HEAD").read()
    msg =  os.popen("/usr/bin/env git pull origin master").read()
    msg = msg.splitlines()
   

    os.popen("cp -rf /home/server/scipy-verifier/unity  /home/verifiers/unity").read()
    os.popen("cp -rf /home/server/scipy-verifier/junit  /home/verifiers/junit").read()
    os.popen("chmod 777 -R /home/verifiers/junit").read()
    os.popen("chmod 777 -R /home/verifiers/unity").read()
    os.popen("chown verifiers:verifiers -R /home/verifiers").read()
    
    os.popen("chmod 777 -R /home/verifiers").read()
    os.popen("chown verifiers:verifiers -R /home/verifiers").read()
    os.popen("chmod +x /home/server/scipy-verifier/installation/boot.sh").read()
    
    
    #stop
    print os.popen("/usr/bin/env python "+folder+"stop_verifiers.py").read()
    
    #start
    os.execl("/usr/bin/env","python",folder+"start_verifiers.py")