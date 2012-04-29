import re
import json
import logging
import doctest
import traceback

from multiprocessing import Process,freeze_support, Queue
from Queue import Empty




def runScipyInstance(jsonrequest,outQueue):
    """ run a new  python instance and  test the code"""
    #laod json data in python object
    try:
        print jsonrequest
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
        tests    = str(jsonrequest["tests"]).replace('"',"'")
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
        numpycall =  re.findall("\( *([a-zA-Z0-9_\.]+|'.*'|\".*\"|\[[^\[\]]*\]|\([^\(\)]*\)) *(,|==) *([a-zA-Z0-9_\.]+|'.*'|\".*\"|\[[^\[\]]*\]|\([^\(\)]*\))(.*)\)",e.source)
        print numpycall
        if len(numpycall)>0:
            print numpycall[0][0]
            print eval(numpycall[0][0])
        
 
output = Queue() 
runScipyInstance(json.dumps({"solution":"import numpy\nimport scipy\nimport scipy.interpolate\n\nx = numpy.arange(10,dtype='float32') * 0.3\ny = numpy.cos(x)\n\nrep = scipy.interpolate.splrep(x,y)\nsol =  scipy.interpolate.splev(0.5,rep)\n","tests":">>> assert_almost_equal('sol1', 0.87752449938946964)\n>>> assert_almost_equal('sol',  0.877524499)\n>>> assert_almost_equal('sol',  0.877524499,15)\n>>> assert_approx_equal(0.12345677777777e-20, 0.1234567e-20)\n>>> assert_array_almost_equal([1.0,2.33333,0],[1.0,2.33339,0], decimal=5)\n>>> assert_array_less([1.0, 1.0, 0], [1.1, 2.0, 0])\n>>> assert_equal(3, 3)\n>>> assert_('bye'=='welcome')\n>>> assert_string_equal('hello', 'hello')\n"}),output)
print output.get()