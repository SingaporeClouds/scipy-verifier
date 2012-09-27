#!/usr/bin/env python
import os
import pwd

folder = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    verifiers_home_dir      = pwd.getpwnam("verifiers").pw_dir
    
    #delete old file
    print os.popen("rm -rf "+verifiers_home_dir+"/java_server").read()
    
    #copy new files
    print os.popen("cp -rf "+folder+"/javaserver  "+verifiers_home_dir+"/javaserver").read()
    
    print os.popen("chown verifiers:verifiers -R "+verifiers_home_dir).read() 
    print os.popen("chmod 777 -R "+verifiers_home_dir).read()
    
    print os.popen("fuser -k 2012/tcp").read()
    
    
    
    
    