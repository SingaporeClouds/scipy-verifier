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
from verifiers.jsp import formatutils
from verifiers.jsp import shellutils
    
def runJSPInstance(jsonrequest,outQueue):
    
    """ run a new  JSP instance and  test the code"""
    os.chdir("/home/verifiers/junit")
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
        logging.info("JSP verifier returning errors =%s", errors)
        responseDict = {'errors': '%s' % errors}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON) 
        
    #os.chdir("/home/verifiers/unity")
    try:
        assertions = formatutils.wrapAssertions(tests.strip()) # was "assertions"
        #formattedTests, resultList = formatutils.format_tests(tests, solution)
        # Update the JSP test file by pasting in the solution code and tests.
        code = formatutils.render_template('java/JSPTester.java', {'parameters':'', 'assertions': assertions}) 
        jspcode = solution.strip()
        compileResult, result = shellutils.compile_jsp_and_get_results(code, jspcode)
    except:
        ExecutionError()
        return
    
    # Create a valid json respose based on the xcodebuild results or error returned.        
    if compileResult['errors']:
        responseDict = {'errors': compileResult['errors']}
    else:
        # it probably compiled, look for test results
        if result:
            responseDict = result
        else: #other unecpected result
            responseDict = {'errors': '%s\n%s' % (compileResult['warnings_and_errors'], result)}
            responseDict['printed'] = compileResult['warnings_and_errors']
    
            # DEBUG - remove later
            responseDict['javac-command'] = compileResult['javac-command']
            responseDict['java-command'] = compileResult['java-command']

    
    responseJSON = json.dumps(responseDict)
    logging.info("JSP verifier returning %s",responseJSON)
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
    runJSPInstance(jsonrequet,out)
    print out.get()