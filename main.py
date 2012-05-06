# !/usr/bin/env python

import re
import json
import logging
import doctest
import traceback
import time
import subprocess
import os
import signal


from gevent import Greenlet
from gserver.routes import Routes
from gserver.request import parse_vals
from gserver.wsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
from Queue import Empty,Queue
from scipyverifier import runScipyInstance,TimeoutException
from threading import Thread

#create routes
routes = Routes()
route = routes.route

#load scipy page
htmlFile = open("scipy.html")
scipy_page_htm =  htmlFile.read()
htmlFile.close()

#load R page
htmlFile = open("R.html")
R_page_htm =  htmlFile.read()
htmlFile.close()

def Command(*cmd,**kwargs):

    '''
       Enables to run subprocess commands in a different thread
       with TIMEOUT option!
       Based on jcollado's solution:
       http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
       and  https://gist.github.com/1306188
    '''

    if kwargs.has_key("timeout"):
        timeout = kwargs["timeout"]
        del kwargs["timeout"]
    else:
        timeout = None
    process = []

    def target(process,out,*cmd,**k):
        process.append(subprocess.Popen(cmd, stdout=subprocess.PIPE,**k))
        out.put(process[0].communicate()[0])
        
    outQueue = Queue()
    args = [process,outQueue]
    args.extend(cmd)
    thread = Thread(target=target, args=args, kwargs=kwargs)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
       process[0].terminate()
       thread.join()
       raise Empty
    return  outQueue.get()

class Worker(Greenlet):
    
    def __init__(self,jsonrequest,out):
        Greenlet.__init__(self)
        self.jsonrequest = jsonrequest
        self.out =  out
        
    def signal_handler(self,signum, frame):
        raise TimeoutException
    
    def signal_handler_2(self,signum, frame):
        print "hack!"
        
    def _run(self):
        signal.signal(signal.SIGALRM, self.signal_handler)
        alarm = signal.alarm(5)   # 5 seconds
        try:
            runScipyInstance(self.jsonrequest,self.out)
        except:
            pass
        signal.signal(signal.SIGALRM, self.signal_handler_2)
        
        
#scipy page handler
@route("^/scipy_test$")
def scipyPage(req):
    return [scipy_page_htm]

#R page handler
@route("^/R_test$")
def RPage(req):
    return [R_page_htm]

#scipy veryfier handler
@route("^/scipy$",method="GET,POST")
def scipyVerifier(request):
    #get post request
    post_data = request.form_data
    try:
        jsonrequest = post_data["jsonrequest"][0]
    except:
        responseDict = {'errors': 'Bad request'}
        responseJSON = json.dumps(responseDict)
        logging.error("Bad request")
        return [responseJSON]
    out = Queue()
    logging.info("Python verifier received: %s",jsonrequest) 
    new_job = Worker(jsonrequest,out)
    new_job.start()
    new_job.join(5)
    try:
        result =  out.get_nowait()
    except Empty:
        s = "Your code took too long to return. Your solution may be stuck "+\
            "in an infinite loop. Please try again."
        result = json.dumps({"errors": s})
        logging.error(s)
        
    return[result]
    
@route("^/r$",method="GET,POST")
def RVerifier(request):
    #get post request
    post_data = request.form_data
    try:
        jsonrequest = post_data["jsonrequest"][0]
    except:
        responseDict = {'errors': 'Bad request'}
        responseJSON = json.dumps(responseDict)
        logging.error("Bad request")
        return [responseJSON]
    try:
        result = Command("/usr/bin/env","python",os.path.join(os.path.dirname(__file__),"rverifier.py"),jsonrequest,timeout=5)
    except Empty:
        s = "Your code took too long to return. Your solution may be stuck "+\
            "in an infinite loop. Please try again."
        result = json.dumps({"errors": s})
        logging.error(s)
    return[result]
    
if __name__ == '__main__':
    print 'Serving on 8080...'
    WSGIServer(('', 8080), routes).serve_forever()