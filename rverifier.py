# -*- coding: utf-8 -*-
import json
import logging
import doctest
import traceback
import sys
from rpy2.robjects import r
from rpy2.rinterface import RRuntimeError
from Queue import Queue
logger = logging.getLogger('rverifie')
hdlr = logging.FileHandler('/var/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

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
    
    def ExecutionError():
        """ catch all the execution error, for the solution and each test """
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
        
    printed = sys.stdout.flush()
    responseDict = {"solved": solved , "results": resultList, "printed":printed}
    return responseDict

if __name__ == '__main__':
    out = Queue()
    jsonrequet = sys.argv[1]
    runRInstance(jsonrequet,out)
    print out.get()
    