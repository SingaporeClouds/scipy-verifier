import re
import json
import logging
import doctest
import traceback
import time
from threading import Thread
from Queue import Empty,Queue
import subprocess
import os
def Command(cmd,**kwargs):
    '''Enables to run subprocess commands in a different thread
       with TIMEOUT option!
       Based on jcollado's solution:
       http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
       and  https://gist.github.com/1306188
    '''
    
    if kwargs.has_key("timeout"):
        timeout = kwargs["timeout"]
        del kwargs["timeout"]
        
    timeout = None
    process = []
    
    def target(cmd,process,out,**k):
        import sys
        import StringIO
        new_stdout = StringIO.StringIO()
        process.append(subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,**k))
        out.put(process[0].communicate()[0])
        
    outQueue = Queue()
    thread = Thread(target=target, args=(cmd,process,outQueue), kwargs=kwargs)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
       process[0].terminate()
       thread.join()
       raise Empty
    return  outQueue.get()
 

print Command("/usr/bin/env python %s %s"%(os.path.join(os.path.dirname(__file__),"scipyverifier.py"),jsonrequest))
