# -*- coding: utf-8 -*-
# !/usr/bin/env python

import re
import json
import logging
import doctest
import traceback
import sys
from Queue import Queue
import StringIO


class TimeoutException(Exception): pass

def runScipyInstance(jsonrequest,outQueue):
    """ run a new  python instance and  test the code"""
    #laod json data in python object
    try:
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
        tests    = str(jsonrequest["tests"])
    except:
        responseDict = {'errors': 'Bad request'}
        logging.error("Bad request")
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return
    
    oldfile = sys.stdout
    sys.stdout = newfile =  StringIO.StringIO()
    
    def ExecutionError():
        """ catch all the execution error, for the solution and each test """
        sys.stdout = oldfile
        errors = traceback.format_exc()
        logging.info("Python verifier returning errors =%s", errors)
        responseDict = {'errors': '%s' % errors}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON) 
        
    try:
        # import numpy testing and execute solution 
        namespace = {}
        compiled = compile("from numpy.testing import *\nimport numpy\nimport scipy", 'submitted code', 'exec')
        exec compiled in namespace
        compiled = compile(solution, 'submitted code', 'exec')
        exec compiled in namespace
        namespace['YOUR_SOLUTION'] = solution.strip()
        namespace['LINES_IN_YOUR_SOLUTION'] = len(solution.strip().splitlines())
    except TimeoutException:
        return
    except:
        ExecutionError()
        return
    
    #get tests
    try:
        test_cases = doctest.DocTestParser().get_examples(tests)
    except TimeoutException:
        return
    except:
        ExecutionError()
        return
    
    results = execute_test_cases(test_cases, namespace,ExecutionError)
    sys.stdout = oldfile
    printed = newfile.getvalue()
    results["printed"] = printed
    responseJSON = json.dumps(results)
    logging.info("Python verifier returning %s",responseJSON)
    outQueue.put(responseJSON)
    
    
def execute_test_cases(testCases, namespace,ExecutionError):
    import sys
    """ run all the tests case """
    
    resultList = []
    solved = True
    for e in testCases:
        correct = True
        #Identify numpy assertions 
        numpyAssertions = "(assert_|assert_almost_equal|assert_approx_equal|assert_array_almost_equal|assert_array_equal|assert_array_less|assert_string_equal|assert_equal)"
        numpycall =  re.findall(numpyAssertions,e.source)
        if len(numpycall)>0:
            call = e.source.strip()
            logging.warning('call: %s', (call,))
            got = True
            correct = True
            #run assertion
            try:
                eval(call, namespace)
            except AssertionError:
                got = False
            except TimeoutException:
                return
            except:
                ExecutionError()
                return
            if not e.want:
                continue
            expected = eval(e.want, namespace)
            if got != expected:
                correct = False
                solved = False
                
        #run other test
        else:
            try:
                call = e.source.strip()
                logging.warning('call: %s', (call,))
                got = eval(call, namespace)
                if not e.want:
                    continue
                expected = eval(e.want, namespace)
            except TimeoutException:
                return
            except:
                ExecutionError()
                return
            if got != expected:
                correct = False
                solved = False
        resultDict = {'call': call, 'expected': expected, 'received': "%(got)s" % {'got': got}, 'correct': correct}
        resultList.append(resultDict)
        
   
    responseDict = {"solved": solved , "results": resultList}
    return responseDict

if __name__ == '__main__':
    import pwd
    import os
    pw_record      = pwd.getpwnam("verifiers")
    user_name      = pw_record.pw_name
    user_home_dir  = pw_record.pw_dir
    user_uid       = pw_record.pw_uid
    user_gid       = pw_record.pw_gid
    os.environ['HOME']     = user_home_dir
    os.environ['LOGNAME']  = user_name
    os.environ['USER']  = user_name
    os.setgid(user_gid)
    os.setuid(user_uid)
    out = Queue()
    jsonrequet = sys.argv[1]
    runScipyInstance(jsonrequet,out)
    print out.get()
    