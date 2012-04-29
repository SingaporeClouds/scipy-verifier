from Queue import Queue
import json
import logging
import doctest
import traceback
import re
def runScipyInstance(jsonrequest,outQueue):
    try:
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
        tests    = str(jsonrequest["tests"])
    except:
        responseDict = {'errors': 'Bad request'}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return
    def ExecutionError():
        errors = traceback.format_exc()
        logging.info("Python verifier returning errors =%s", errors)
        responseDict = {'errors': '%s' % errors}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
    try:
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
    resultList = []
    solved = True
    for e in testCases:
        #numpy assertion
        numpyAssertions = "(assert_|assert_almost_equal|assert_approx_equal|assert_array_almost_equal|assert_array_equal|assert_array_less|assert_string_equal|assert_equal)"
        print e.source
        numpycall =  re.findall(numpyAssertions+"\(([a-zA-Z0-9_ ]+|\".*\"|\[.*\]|\(.*\)|\{.*\})(,|==)([a-zA-Z0-9_ ]+|\".*\"|\[.*\]|\(.*\)|\{.*\})(.*)\)",e.source)
        #\((([a-zA-Z0-9]+|\[.*\]|\(.*\)|{.*}),?)*\)
        print numpycall
        if len(numpycall)>0:
            call = e.source.strip()
            try:
                got = eval(numpycall[0][1],namespace)
                expected = eval(numpycall[0][3],namespace)
            except:
                ExecutionError()
                return
            assertion_call = numpycall[0][0]+"(%s%s%s)"%(str(got),numpycall[0][2],str(expected))
            correct = True
            try:
                eval(assertion_call, namespace)
            except AssertionError:
                correct = False
                solved = False
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
    return resultList, solved

out = Queue()
runScipyInstance("{\"solution\":\"import numpy\\nimport scipy\\nimport scipy.interpolate\\n\\nx = numpy.arange(10,dtype='float32') * 0.3\\ny = numpy.cos(x)\\n\\nrep = scipy.interpolate.splrep(x,y)\\nsol =  scipy.interpolate.splev(0.5,rep)\\n\",\"tests\":\">>> assert_almost_equal(sol, sol)\"}",out)
print out.get()