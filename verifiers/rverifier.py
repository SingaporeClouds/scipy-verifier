# -*- coding: utf-8 -*-
# !/usr/bin/env python

import json
import logging
import doctest
import traceback
import sys
from rpy2.robjects import r
from rpy2.rinterface import RRuntimeError
from Queue import Queue
import StringIO

def runRInstance(jsonrequest,outQueue):
    """ run a new  python instance and  test the R code"""
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
        # import RUnit , testthat and execute solution 
        r("library('RUnit')")
        r("library('testthat')")
        r(solution)
    except:
        ExecutionError()
        return
    
    #get tests
    try:
        test_cases = doctest.DocTestParser().get_examples(tests)
    except:
        ExecutionError()
        return
    
    results = execute_test_cases(test_cases,ExecutionError)
    sys.stdout = oldfile
    printed = newfile.getvalue()
    results["printed"] = printed
    responseJSON = json.dumps(results)
    logging.info("Python verifier returning %s",responseJSON)
    outQueue.put(responseJSON)
    
    
    
def execute_test_cases(testCases,ExecutionError):
    """ run all the tests case """
    resultList = []
    solved = True
    for e in testCases:
        correct = True
        call = e.source.strip()
        try:
            got = r(call)
            try:
                got = got[0]
            except:
                got = True
        except RRuntimeError:
            got = False
        except:
            ExecutionError()
        if not e.want:
            continue
        try:
            expected = eval(e.want)
        except:
            ExecutionError()
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
    runRInstance(jsonrequet,out)
    print out.get()
    