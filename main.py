# !/usr/bin/env python

import re
import json
import logging
import doctest
import traceback

from multiprocessing import Process,freeze_support, Queue
from Queue import Empty

from gserver.routes import Routes
from gserver.request import parse_vals
from gserver.wsgi import WSGIServer

#create routes
routes = Routes()
route = routes.route

#load main page
htmlFile = open("index.html")
main_page_htm =  htmlFile.read()
htmlFile.close()

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
    #queue for comunication with a new instance
    outQueue = Queue()  
    #Create a instance for run the code
    instance = Process(target=runScipyInstance, args=(jsonrequest,outQueue))
    instance.start()
    
    try:
        result = outQueue.get(True,5)
        if instance.is_alive():
            instance.terminate()
    except Empty:
        if instance.is_alive():
            instance.terminate()
        s = "Your code took too long to return. Your solution may be stuck "+\
            "in an infinite loop. Please try again."
        result = json.dumps({"errors": s})
        logging.error(s)
        
    return[result]

def runScipyInstance(jsonrequest,outQueue):
    """ run a new  python instance and  test the code"""
    #laod json data in python object
    try:
        print jsonrequest
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
        tests    = str(jsonrequest["tests"])
    except:
        responseDict = {'errors': 'Bad request'}
        logging.error("Bad request")
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return
    
    def ExecutionError():
        """ catch all the execution error, for the solution and each test """
        errors = traceback.format_exc()
        logging.info("Python verifier returning errors =%s", errors)
        responseDict = {'errors': '%s' % errors}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        
    try:
        # import numpy testing and execute solution 
        namespace = {}
        compiled = compile("from numpy.testing import *", 'submitted code', 'exec')
        exec compiled in namespace
        compiled = compile(solution, 'submitted code', 'exec')
        exec compiled in namespace
        namespace['YOUR_SOLUTION'] = solution.strip()
        namespace['LINES_IN_YOUR_SOLUTION'] = len(solution.strip().splitlines())
    except:
        ExecutionError()
        return
    
    #get tests
    try:
        test_cases = doctest.DocTestParser().get_examples(tests)
    except:
        ExecutionError()
        return
    
    results = execute_test_cases(test_cases, namespace,ExecutionError)
    
    responseJSON = json.dumps(results)
    logging.info("Python verifier returning %s",responseJSON)
    
    outQueue.put(responseJSON)
    
def execute_test_cases(testCases, namespace,ExecutionError):
    import sys
    """ run all the tests case """
    
    resultList = []
    solved = True
    for e in testCases:
        #Identify numpy assertions 
        numpyAssertions = "(assert_|assert_almost_equal|assert_approx_equal|assert_array_almost_equal|assert_array_equal|assert_array_less|assert_string_equal|assert_equal)"
        numpycall =  re.findall(numpyAssertions+"\( *([a-zA-Z0-9_\.]+|'.*'|\".*\"|\[[^\[\]]*\]|\([^\(\)]*\)) *(,|==) *([a-zA-Z0-9_\.]+|'.*'|\".*\"|\[[^\[\]]*\]|\([^\(\)]*\))(.*)\)",e.source)
        print numpycall
        print e.source
        if len(numpycall)>0:
            call = e.source.strip()
            try:
                got            = eval(numpycall[0][1],namespace)
                expected      =  eval(numpycall[0][3],namespace)
            except:
                ExecutionError()
                return
            assertion_call = numpycall[0][0]+"(%s%s%s"%(str(got),numpycall[0][2],str(expected)) + numpycall[0][4] + ")"
            correct = True
            #run assertion
            try:
                eval(assertion_call, namespace)
            except AssertionError:
                correct = False
                solved = False
            except:
                ExecutionError()
                return
                
        #run other test
        else:
            try:
                call = e.source.strip()
                logging.warning('call: %s', (call,))
                got = eval(call, namespace)
                if not e.want:
                    continue
                expected = eval(e.want, namespace)
            except:
                ExecutionError()
                return
            correct = True
            if got == expected:
                correct = True
            else:
                correct = False
                solved = False
        resultDict = {'call': call, 'expected': expected, 'received': "%(got)s" % {'got': got}, 'correct': correct}
        resultList.append(resultDict)
        
    printed = sys.stdout.flush()
    responseDict = {"solved": solved , "results": resultList, "printed":printed}
    return responseDict
  
if __name__ == '__main__':
    freeze_support()
    print 'Serving on 8080...'
    WSGIServer(('', 8080), routes).serve_forever()