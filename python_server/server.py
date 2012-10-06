# -*- coding: utf-8 -*-

#!/usr/bin/env python

import sys
import os
import json
import logging
import subprocess
from Queue import Empty,Queue
from threading import Thread
import base64
import socket 
import tornado.ioloop
import tornado.web

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(folder)


os.chdir("/home/server/scipy-verifier")

verifiers_dict = {"r":"R_verifier.py",
                  "c" : "c_verifier.py",
                  "oc":"oc_verifier.py",
                  "scipy":"scipy_verifier.py",
                  "python":"python_verifier.py",
                  "oldjsp":"jsp_verifier.py",
                  "jsp":None,
                  "java":None,
                  "ruby":None,
                  }
java_list = ["java","jsp","ruby"]


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



def SendToJava(verifier,jsonrequest):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    s.connect(("localhost", 2012))  
    
    message = verifier+" "*(10-len(verifier)) + jsonrequest
    message = base64.b64encode(message)
    
    count = len(message)
    msb, lsb = divmod(count, 256) # split to two bytes
    s.send(chr(msb))
    s.send(chr(lsb))
    s.send(message)
    
    data =  s.recv(102400)
    
    s.close()
    response =  repr(data).decode('UTF-8')
    response = base64.b64decode(response)
    response = response[response.index("{"):].strip("'")
    if response.startswith("{{"):
        response = response[1:]
    return response



class CommitHandler(tornado.web.RequestHandler):
    def get(self):
        commit = os.popen("git rev-parse HEAD").read()
        mini_commit = commit[0:10]
        url = "<a href='https://github.com/SingaporeClouds/scipy-verifier/commit/"+commit+"'>"+mini_commit+"</a>"
        self.set_header("Content-type","text/html")
        self.write("Commit : "+url)
        self.finish()
    
class VerifierHandler(tornado.web.RequestHandler):
    
    @tornado.web.asynchronous
    def get(self,verifierName):
        Thread(target=self.verifier, args=("GET", verifierName)).start()
        
    @tornado.web.asynchronous
    def post(self,verifierName):
        Thread(target=self.verifier, args=("POST", verifierName)).start()
        
    
    def verifier(self,method,verifierName=None):
        
        run = True
        if not verifierName in  verifiers_dict:
            result = {'errors': 'verifier not exist'}
            logging.error("verifier not found")
            run = False
        else:
            jsonrequest = self.get_argument("jsonrequest", None)
            if jsonrequest!=None:
                if method=="GET":
                    try:
                        jsonrequest = base64.b64decode(jsonrequest)
                    except:
                        result = {'errors': 'Bad request'}
                        logging.error("Bad request")
                        run = False   
            else :
                result = {'errors': 'Bad request'}
                logging.error("Bad request")
                run = False
        
        
        vcallback = self.get_argument("vcallback", None)
        
        if run:
            if verifierName in java_list:
                try:
                    result = SendToJava(verifierName,jsonrequest)
                except:
                    result = json.dumps({"errors":"Internal Server Error"})
                print str(result)
                json.loads(unicode(result))
                if  vcallback!=None:
                    result = vcallback+"("+result+")"
                self.set_header("Content-type","text/plain")
                self.write(result)
                self.finish()
                return
            else:
                try:
                    result = json.loads(Command("/usr/bin/env","python",folder+"/verifiers/%s"%verifiers_dict[verifierName],jsonrequest,timeout=5))
                except Empty:
                    s = "Your code took too long to return. Your solution may be stuck "+\
                        "in an infinite loop. Please try again."
                    result = {"errors": s}
                    logging.error(s)
                
        result = json.dumps(result)
        
        if  vcallback!=None:
            result = vcallback+"("+result+")"
        
        self.set_header("Content-type","text/plain")
        self.write(result)
        self.finish()
    
    
class TestHandler(tornado.web.RequestHandler):
    def get(self,filename):
        self.set_header("Content-type","text/html")
        try:
            _file = open(folder +"/testers/"+filename+".html")
        except:
            self.write("Tester page not found")
            return
        
        content = _file.read()
        _file.close()
            
        self.write(content)

application = tornado.web.Application([
    (r"^/current/commit$", CommitHandler),
    (r"^/test/([a-zA-Z0-9_]+)", TestHandler),                                
    (r"^/([a-zA-Z0-9_]+)", VerifierHandler),
])

if __name__ == "__main__":
    #sys.stderr = open(folder+"/error_log","a")
    #sys.stdout = open(folder+"/log","a")
    
    application.listen(80)
    print 'Serving on 80...'
    tornado.ioloop.IOLoop.instance().start()
    