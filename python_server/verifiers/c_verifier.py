import json
import logging
import re
import uuid
import os
import sys
import pwd
from Queue import Queue
import subprocess

test_header = """#include <setjmp.h>
#include "unity.h"
#include "%s"

#define EXPECT_ABORT_BEGIN \\
    if (TEST_PROTECT())    \\
    {

#define VERIFY_FAILS_END                                                       \\
    }                                                                          \\
    Unity.CurrentTestFailed = (Unity.CurrentTestFailed == 1) ? 0 : 1;          \\
    if (Unity.CurrentTestFailed == 1) {                                        \\
      SetToOneMeanWeAlreadyCheckedThisGuy = 1;                                 \\
      UnityPrint("[[[[ Previous Test Should Have Failed But Did Not ]]]]");    \\
      UNITY_OUTPUT_CHAR('\\n');                                                 \\
    }

#define VERIFY_IGNORES_END                                                     \\
    }                                                                          \\
    Unity.CurrentTestFailed = (Unity.CurrentTestIgnored == 1) ? 0 : 1;         \\
    Unity.CurrentTestIgnored = 0;                                              \\
    if (Unity.CurrentTestFailed == 1) {                                        \\
      SetToOneMeanWeAlreadyCheckedThisGuy = 1;                                 \\
      UnityPrint("[[[[ Previous Test Should Have Ignored But Did Not ]]]]");   \\
      UNITY_OUTPUT_CHAR('\\n');                                                 \\
    }

int SetToOneToFailInTearDown;
int SetToOneMeanWeAlreadyCheckedThisGuy;

void setUp(void)
{
  SetToOneToFailInTearDown = 0;
  SetToOneMeanWeAlreadyCheckedThisGuy = 0;
}

void tearDown(void)
{
  if (SetToOneToFailInTearDown == 1)
    TEST_FAIL_MESSAGE("<= Failed in tearDown");
  if ((SetToOneMeanWeAlreadyCheckedThisGuy == 0) && (Unity.CurrentTestFailed > 0))
  {
    UnityPrint("[[[[ Previous Test Should Have Passed But Did Not ]]]]");
    UNITY_OUTPUT_CHAR('\\n');
  }
}"""


def run_c_instance(jsonrequest, outQueue):
    """ run a C instance and  test the code"""
    #laod json data in python object
    try:
        jsonrequest = json.loads(jsonrequest)
        solution = str(jsonrequest["solution"])
        tests = str(jsonrequest["tests"])
    except BaseException:
        responseDict = {'errors': 'Bad request'}
        logging.error("Bad request")
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return

    resultList = []
    solved = False

    uid = uuid.uuid4()
    test_path = '/var/local/singpath_verifier/unity/test/'
    if not os.path.isdir(test_path):
        os.mkdir(test_path)
    src_file = test_path + 'CSolution_%s.h' % uid
    test_file = test_path + 'CSolution_%s.c' % uid

    _solution = open(src_file, "w+")
    _solution.write(solution)
    _solution.close()

    _test = open(test_file, "w+")
    _test.write(test_header % ('CSolution_%s.h' % uid))
    _test.write(tests)
    _test.close()

    os.chdir("/var/local/singpath_verifier/unity")
    out_path = "/var/local/singpath_verifier/unity/out"
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    cmd = "make TARGET_BASE=%s" % ('CSolution_%s' % uid)
    cmd = cmd.split()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=False)
    p.wait()
    stdout, stderr = p.communicate()
    #get test results
    stdout = stdout.splitlines()[5:-3]
    stderr = stderr.splitlines()[0:-2]
    if len(stderr) > 0:
        for i in range(len(stderr)):
            stderr[i] = stderr[i].replace("test/%s" % ('CSolution_%s.c' % uid),"Tests").\
                replace("test/%s" % ('CSolution_%s.h' % uid), "Solution")
        stderr = "\n".join(stderr)
        responseDict = {'errors': stderr}
        responseJSON = json.dumps(responseDict)
        outQueue.put(responseJSON)
        return

    if len(stdout) > 0:
        solved = True

    for i in range(len(stdout)):
        parameters = map(lambda x: x.strip(), stdout[i].split(":"))
        if len(parameters) < 3:
            continue
        parameters = parameters[2:]
        test_name = parameters[0];
        test_pass = True if parameters[1] == "PASS" else False
        if not test_pass:
            solved = False
            try:
                expected, got = map(lambda x: x.strip(), re.findall("Expected(.*)Was(.*)", parameters[2])[0])
                got = "%s - %s" % (got, parameters[2])
            except BaseException:
                expected, got = "", ""
        else:
            expected, got = "", ""
        resultDict = {'call': test_name, 'expected': expected, 'received': "%s" % got, 'correct': test_pass}
        resultList.append(resultDict)

    responseDict = {"solved": solved, "results": resultList, "printed":None}
    responseJSON = json.dumps(responseDict)
    outQueue.put(responseJSON)



if __name__ == '__main__':
    pw_record = pwd.getpwnam("verifiers")
    user_name = pw_record.pw_name
    user_home_dir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    os.environ['HOME'] = user_home_dir
    os.environ['LOGNAME'] = user_name
    os.environ['USER'] = user_name
    os.environ['LANGUAGE'] = "en_US.UTF-8"
    os.environ['LANG'] = "en_US.UTF-8"
    os.environ['LC_ALL'] = "en_US.UTF-8"
    os.setgid(user_gid)
    os.setuid(user_uid)
    jsonrequet = sys.argv[1]
    out = Queue()
    run_c_instance(jsonrequet, out)
    print out.get()