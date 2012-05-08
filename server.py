# -*- coding: utf-8 -*-

#!/usr/bin/env python

import sys
folder = "/home/server/scipy-verifier/"
sys.path.append(folder)

import json
import logging
import subprocess
from gserver.routes import Routes
from gserver.request import parse_vals
from gserver.wsgi import WSGIServer
from Queue import Empty,Queue
from threading import Thread


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
        process.append(subprocess.Popen(cmd,stdout=subprocess.PIPE,**k))
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


#create routes
routes = Routes()
route = routes.route

#load scipy page
htmlFile = open(folder+"/html/scipy.html")
scipy_page_htm =  htmlFile.read()
htmlFile.close()

#load R page
htmlFile = open(folder+"/html/R.html")
R_page_htm =  htmlFile.read()
htmlFile.close()
       
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
    try:
        result = Command("/usr/bin/env","python",folder+"/verifiers/scipy_verifier.py",jsonrequest,timeout=5)
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
        result = Command("/usr/bin/env","python",folder+"/verifiers/R_verifier.py",jsonrequest,timeout=5)
    except Empty:
        s = "Your code took too long to return. Your solution may be stuck "+\
            "in an infinite loop. Please try again."
        result = json.dumps({"errors": s})
        logging.error(s)
    return[result]
    
if __name__ == '__main__':
    sys.stderr = open(folder+"/error_log","a")
    sys.stdout = open(folder+"/log","a")
    print 'Serving on 80...'
    WSGIServer(('', 80), routes).serve_forever()