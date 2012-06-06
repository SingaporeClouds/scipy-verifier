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
import base64

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

#load Objetive C page
htmlFile = open(folder+"/html/ObjetiveC.html")
ObjetiveC_page_htm =  htmlFile.read()
htmlFile.close()

#load  C page
htmlFile = open(folder+"/html/C.html")
C_page_htm =  htmlFile.read()
htmlFile.close()

#scipy page handler
@route("^/test/scipy$")
def scipyPage(req):
    return [scipy_page_htm]

#R page handler
@route("^/test/r$")
def RPage(req):
    return [R_page_htm]

#scipy page handler
@route("^/test/oc$")
def ObjetiveCPage(req):
    return [ObjetiveC_page_htm]

#scipy page handler
@route("^/test/c$")
def CPage(req):
    return [C_page_htm]

verifiers_dict = {"r":"R_verifier.py",
                  "c" : "c_verifier.py",
                  "oc":"oc_verifier.py",
                  "scipy":"scipy_verifier.py"
                  }

@route("^/(?P<name>\w+)$",method="GET,POST")
def verifier(request,name=None):
    get_data  = request.query_data
    post_data = request.form_data
    run = True
    if not name in  verifiers_dict:
        result = {'errors': 'verifier not exist'}
        logging.error("verifier not found")
    else:    
        #get post request
        if "jsonrequest" in post_data:
            jsonrequest = post_data["jsonrequest"][0]
        elif "jsonrequest" in get_data:
            try:
                jsonrequest = base64.b64decode(get_data["jsonrequest"][0])
            except:
                result = {'errors': 'Bad request'}
                logging.error("Bad request")
                run = False
        else :
            result = {'errors': 'Bad request'}
            logging.error("Bad request")
            run = False
        if run:
            try:
                result = json.loads(Command("/usr/bin/env","python",folder+"/verifiers/%s"%verifiers_dict[name],jsonrequest,timeout=5))
            except Empty:
                s = "Your code took too long to return. Your solution may be stuck "+\
                    "in an infinite loop. Please try again."
                result = {"errors": s}
                logging.error(s)
    
    if  "key" in get_data:
        result["key"] = get_data["key"];
    result = json.dumps(result)
    if  "vcallback" in get_data:
        callback = get_data["vcallback"][0]
        return[callback+"("+result+")"]
    return[result]
        
if __name__ == '__main__':
    sys.stderr = open(folder+"/error_log","a")
    sys.stdout = open(folder+"/log","a")
    print 'Serving on 80...'
    WSGIServer(('', 80), routes).serve_forever()