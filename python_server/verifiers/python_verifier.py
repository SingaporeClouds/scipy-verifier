# !/usr/bin/env python

import os
import logging
import doctest
import traceback
import json
import sys
import StringIO
from Queue import Queue
import pwd
import re
    
def runPythonInstance(jsonrequest,outQueue):
    
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
        compiled = compile("", 'submitted code', 'exec')
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
    try:
        results,solved = execute_test_cases(test_cases, namespace)
    except:
        ExecutionError()
        return
        
    sys.stdout = oldfile
    printed = newfile.getvalue()
    
    responseDict = {"solved": solved , "results": results, "printed":printed}
    responseJSON = json.dumps(responseDict)
    logging.info("Python verifier returning %s",responseJSON)
    outQueue.put(responseJSON)

#Refactor for better readability.
def execute_test_cases(testCases, namespace):
    resultList = []
    solved = True
    
    for e in testCases:
        if not e.want:
            exec e.source in namespace
            continue
        call = e.source.strip()
        logging.warning('call: %s', (call,))
        got = eval(call, namespace)
        expected = eval(e.want, namespace)
        correct = True
        if got == expected:
            correct = True
        else:
            correct = False
            solved = False
        resultDict = {'call': call, 'expected': expected, 'received': "%(got)s" % {'got': got}, 'correct': correct}
        resultList.append(resultDict)
    return resultList, solved


def run_python_code(jsonrequest,outQueue):
    
    """ run  python codes without tests"""
    
    #laod json data in python object
    try:
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
    except:
        responseDict = {'errors': 'Bad request'}
        logging.error("Bad request")
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return
    
    oldfile = sys.stdout
    oldfile2 = sys.stderr
    sys.stderr = sys.stdout = newfile =  StringIO.StringIO()
    
    def ExecutionError():
        """ catch all the execution error, for the solution and each test """
        sys.stdout = oldfile
        sys.stderr = oldfile2
        errors = traceback.format_exc()
        logging.info("Python verifier returning errors =%s", errors)
        user_errors = re.findall("File \"submitted code\".*", errors,re.S)
        if user_errors:
            errors = user_errors[0]
        responseDict = {'errors': '%s' % (newfile.getvalue()+errors)}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON) 
        
    try:
        # import numpy testing and execute solution 
        namespace = {}
        compiled = compile("", 'submitted code', 'exec')
        exec compiled in namespace
        compiled = compile(solution, 'submitted code', 'exec')
        exec compiled in namespace
        namespace['YOUR_SOLUTION'] = solution.strip()
        namespace['LINES_IN_YOUR_SOLUTION'] = len(solution.strip().splitlines())
    except:
        ExecutionError()
        return

        
    sys.stdout = oldfile
    sys.stderr = oldfile2
    printed = newfile.getvalue()
    
    responseDict = {"printed":printed}
    responseJSON = json.dumps(responseDict)
    logging.info("Python verifier returning %s",responseJSON)
    outQueue.put(responseJSON)
    
    
if __name__ == '__main__':
    pw_record              = pwd.getpwnam("verifiers")
    user_name              = pw_record.pw_name
    user_home_dir          = pw_record.pw_dir
    user_uid               = pw_record.pw_uid
    user_gid               = pw_record.pw_gid
    os.environ['HOME']     = user_home_dir
    os.environ['LOGNAME']  = user_name
    os.environ['USER']     = user_name
    os.setgid(user_gid)
    os.setuid(user_uid)
    out = Queue()
    jsonrequet = sys.argv[1]
    try:
        only_play =  int(sys.argv[2])
    except:
        only_play = 0
        
    if not only_play:
        runPythonInstance(jsonrequet,out)
    else:
        run_python_code(jsonrequet,out)
    print out.get()