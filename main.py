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

#create routes
routes = Routes()
route = routes.route

#load main page
htmlFile = open("index.html")
main_page_htm =  htmlFile.read()
htmlFile.close()


class Worker(Greenlet):
    
    def __init__(self,jsonrequest,out):
        Greenlet.__init__(self)
        self.jsonrequest = jsonrequest
        self.out =  out
    
    def signal_handler(self,signum, frame):
        raise TimeoutException

    def _run(self):
        signal.signal(signal.SIGALRM, self.signal_handler)
        signal.alarm(5)   # Ten seconds
        try:
            runScipyInstance(self.jsonrequest,self.out)
        except:
            return
        
#main page handler
@route("^/$")
def mainPage(req):
    return [main_page_htm]

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
    
    logging.info("Python verifier received: %s",jsonrequest) 
    
    out = Queue()
    new_job = Worker(jsonrequest,out)
    new_job.start()
    try:
        result =  out.get(True, 5)
    except Empty:
        s = "Your code took too long to return. Your solution may be stuck "+\
            "in an infinite loop. Please try again."
        result = json.dumps({"errors": s})
        logging.error(s)
        
    return[result]

if __name__ == '__main__':
    print 'Serving on 8080...'
    WSGIServer(('', 8080), routes).serve_forever()