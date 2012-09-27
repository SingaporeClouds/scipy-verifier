#!/usr/bin/python
import json
# start the server
import os,sys,pwd
folder = os.path.dirname(os.path.abspath(__file__))
verifiers_home_dir = pwd.getpwnam("verifiers").pw_dir
#clean ports
print "closing ports"
print os.popen("fuser -k 80/tcp").read()
print os.popen("fuser -k 2012/tcp").read()
#compile and run java server
print os.popen("python "+folder+"/compile_java.py").read()

#run python server
output = str(os.spawnv(os.P_NOWAIT,sys.executable,("python",folder+"/python_server/server.py","")))
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
os.chdir(verifiers_home_dir+"/javaserver/build/classes/")
java_pid = str(os.spawnv(os.P_NOWAIT,"/usr/bin/java",("java","-cp",":"+verifiers_home_dir+"/javaserver/libs/*","com/singpath/javabox/Server")))



pids = {"java":java_pid,"python":output}
os.chdir("/tmp")
_file = open("singpath_pids","w+")
_file.write(json.dumps(pids))
_file.close()
print "server opened"