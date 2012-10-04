#!/usr/bin/env python
import os
import pwd

folder = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    verifiers_home_dir      = pwd.getpwnam("verifiers").pw_dir
    
    #delete old file
    print os.popen("rm -rf "+verifiers_home_dir+"/java_server").read()
    
    #copy new files
    print os.popen("cp -rf "+folder+"/javaserver  "+verifiers_home_dir).read()
    
    print os.popen("chown verifiers:verifiers -R "+verifiers_home_dir).read() 
    print os.popen("chmod 777 -R "+verifiers_home_dir).read()
    
    print os.popen("fuser -k 2012/tcp").read()
    
    pw_record      = pwd.getpwnam("verifiers")
    user_name      = pw_record.pw_name
    user_home_dir  = pw_record.pw_dir
    user_uid       = pw_record.pw_uid
    user_gid       = pw_record.pw_gid
    os.environ['HOME']     = user_home_dir
    os.environ['LOGNAME']  = user_name
    os.environ['USER']     = user_name
    os.environ['LANGUAGE'] = "en_US.UTF-8"
    os.environ['LANG']     = "en_US.UTF-8"
    os.environ['LC_ALL']   = "en_US.UTF-8"
    os.setgid(user_gid)
    os.setuid(user_uid)
    
    os.chdir(verifiers_home_dir+"/javaserver")
    
    print os.popen("ant compile").read()
    
    
    