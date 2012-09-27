#!/usr/bin/env python
import os
import logging
import json
import pwd
log = logging.getLogger("update")
folder = os.path.dirname(os.path.abspath(__file__))
parent_folder           = folder.replace("installation","")

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.NOTSET,filename=os.path.join(parent_folder,"update.log"))
    verifiers_home_dir      = pwd.getpwnam("verifiers").pw_dir
    
    #load singpath_ini
    try:
        _file = open(parent_folder+"singpath.ini")
        content = _file.read()
        _file.close()
        singpath_ini = json.loads(content.strip())
    except:
        singpath_ini = {}
    
    if singpath_ini.get("auto_update",True)==False:
        log.info("Auto update option is disabled")
        exit(0)
        
    #delete old file
    log.info(os.popen("rm -rf "+verifiers_home_dir+"/unity").read())
    log.info(os.popen("rm -rf "+verifiers_home_dir+"/junit").read())
    
    #cd 
    os.chdir(parent_folder)
    
    #git pull
    log.info(os.popen("/usr/bin/env git reset --hard HEAD").read())
    msg =  os.popen("/usr/bin/env git pull origin master").read()
    log.info(msg)
    msg = msg.splitlines()
   

    log.info(os.popen("cp -rf "+parent_folder+"unity  "+verifiers_home_dir+"/unity").read())
    log.info(os.popen("cp -rf "+parent_folder+"junit  "+verifiers_home_dir+"/junit").read())
    
    log.info(os.popen("chown verifiers:verifiers -R "+verifiers_home_dir).read()) 
    log.info(os.popen("chmod 777 -R "+verifiers_home_dir).read())

    log.info(os.popen("chmod +x "+folder+"/boot.sh").read())
    
    
    #stop
    log.info(os.popen("/usr/bin/env python "+parent_folder+"stop_verifiers.py").read())
    
    #start
    log.info(os.execl("/usr/bin/env","python",parent_folder+"start_verifiers.py"))