#!/usr/bin/env python
import os
folder = os.path.dirname(__file__).replace("installation","")

if __name__=="__main__":
    #cd
    os.chdir(folder)
    #stop
    print os.popen("/usr/bin/env python "+folder+"stop.py").read()
    #git pull
    print os.popen("/usr/bin/env git pull").read()
    #start
    print os.popen("/usr/bin/env python "+folder+"start.py").read()