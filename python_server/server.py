#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import time
import urllib2
from helpers.disk_cleaner import remove_old_file


FOLDER = os.path.dirname(os.path.realpath(__file__))


VERIFIERS_DICT = {
    "r":"R_verifier.py",
    "c" : "c_verifier.py",
    "oc":"oc_verifier.py",
    "scipy":"scipy_verifier.py",
    "python":"python_verifier.py",
    "oldjsp":"jsp_verifier.py",
    "angular": None,
    "jsp":None,
    "java":None,
    "ruby":None,
    "js":None,
}

PYTHON_TESTS = {
    "scipy": {
        "solution": (
                "import scipy.interpolate\nx = numpy.arange(10,dtype='float32') * 0.3\n"
                "y = numpy.cos(x)\nrep = scipy.interpolate.splrep(x,y)\n"
                "sol =  scipy.interpolate.splev(0.5,rep)"
        ),
        "tests": ">>> assert_almost_equal(sol, 0.87752449938946964)\nTrue"
    },

    "oc": {
        "solution": (
            "int b=2;\nfloat f = 123.45;\ndouble inches = 3*2;\n"
            "NSString *string1 = @\"This string is immutable\";"
        ),
        "tests": (
            "AssertEquals(2, b);\nint expected_b = 2;\nAssertEquals(expected_b, b);\n"
            "AssertEquals((float)123.45, f);\nAssertEquals([NSString stringWithString:@\""
            "This string is immutable\"], string1);"
        )
    },
    "c": {
        "solution": (
            "int sum(int a, int b){return a+b;}\nchar *message = \"Hello world!!!\";\n"
            "const char *testStrings[] = { \"foo\", \"boo\", \"woo\", \"zoo\" };"
        ),
        "tests": (
            "void test_sum(void){TEST_ASSERT(5==sum(2,3));}\n"
            "void test_hello_world(void){TEST_ASSERT_EQUAL_STRING(message, \"Hello world!!!\");}"
            "\nvoid testNotEqualStringArray1(void){ const char *expStrings[] = { \"foo\","
            " \"boo\", \"woo\", \"zoo\" };"
            "\nTEST_ASSERT_EQUAL_STRING_ARRAY(expStrings, testStrings, 4);}"
        )
    },
    "r": {
        "solution": "factorial <- function(n){\n return(6);}",
        "tests": ">>> checkEquals(6, factorial(3))\nTrue"
    },
    "python": {
        "solution": "number = 2\nwizard = 'Oz'\ndef addOne(x):\n return x+1",
        "tests": ">>> number\n 2\n>>> wizard\n 'Oz'\n>>> addOne(2)\n  3"
    }
}

PYTHON_RESULTS = {
    "python": {
        'solved': True,
        'results': [
            {
                'expected': 2,
                'received': '2',
                'call': 'number',
                'correct': True
            },
            {
                'expected': 'Oz',
                'received': 'Oz',
                'call': 'wizard',
                'correct': True
            },
            {
                'expected': 3,
                'received': '3',
                'call': 'addOne(2)',
                'correct': True
            }
        ],
        'printed': ''
    },

    "r": {
        'solved': True,
        'results': [
            {
                'expected': True,
                'received': 'True',
                'call': 'checkEquals(6, factorial(3))',
                'correct': True
            }
        ],
        'printed': ''
    },

    'c': {
        'solved': True,
        'results': [
            {
                'expected': '',
                'received': '',
                'call': 'test_sum',
                'correct': True
            },
            {
                'expected': '',
                'received': '',
                'call': 'test_hello_world',
                'correct': True
            },
            {
                'expected': '',
                'received': '',
                'call': 'testNotEqualStringArray1',
                'correct': True
            }
        ],
        'printed': None
    },

    'scipy': {
        'solved': True,
        'results': [
            {
                'expected': True,
                'received': 'True',
                'call': 'assert_almost_equal(sol, 0.87752449938946964)',
                'correct': True
            }
        ],
        'printed': ''
    },

    'oc': {
        'solved': True,
        'results': [
            {
                'expected': '2',
                'received': '2',
                'call': 'AssertEquals(2, b);',
                'correct': True
            },
            {
                'expected': '2',
                'received': '2',
                'call': 'AssertEquals(expected_b, b);',
                'correct': True
            },
            {
                'expected': '123.45',
                'received': '123.45',
                'call': 'AssertEquals((float)123.45, f);',
                'correct': True
            },
            {
                'expected': '"This string is immutable"',
                'received': '"This string is immutable"',
                'call': 'AssertEquals([NSString stringWithString:'\
                    '@"This string is immutable"], string1);',
                'correct': True
            }
        ],
        'printed': ''
    }
}

JAVA_TESTS = {
    "java": {
        "solution": "int a=1;\nint b=2;",
        "tests": "assertEquals(1,a);\nassertEquals(2,b);"},

    "ruby": {
        "solution": "a = 1\nb = 2",
        "tests": "assert_equal(1,a)\nassert_equal(2,b)"
    },
    "js": {
        "solution": "a=1;\nb=2;",
        "tests": "assert_equal(1,a);\nassert_equal(2,b);"
    },
    "jsp": {
        "solution": """<%@ page import="java.util.*, java.text.*" %>
    <HTML>
    <HEAD>
    <TITLE>Hello Pineapples</TITLE>
    </HEAD>
    <BODY>
    <H1>Hello World</H1>
    <TABLE>
    <TR>
    <TD>
    <P>
    This is an <B>embedded</B> table
    </P>
    </TD>
    </TR>
    <TR>
    <TD>
    The request parameter 'fruit' has a value of <%= request.getParameter("fruit") %>
    </TD>
    </TR>
    </TABLE>
    Today is: <%= new SimpleDateFormat("dd/MM/yyyy").format(new Date()) %>
    </BODY>
    </HTML>""",
        'tests': """String expectedDate = new SimpleDateFormat("dd/MM/yyyy").format(new Date());
    Document response = page.get();
    assertEquals(false,response.html().indexOf("Hello Pineapples") == -1);
    assertEquals(false,response.html().indexOf("Today is: "+expectedDate)==-1);
    response = page.get("fruit", "guava");
    assertEquals(false,response.html().indexOf("The request parameter 'fruit' has a value of guava")==-1);
    assertEquals("embedded",response.select("table tr td p b").html());"""
    }
}

JAVA_RESULTS = {
    "ruby": (
        '{"solved":true,"results":[{"expected":"","received":"","call":"assert_equal(1,a)",'
        '"correct":true},{"expected":"","received":"","call":"assert_equal(2,b)","correct":true}]'
        ',"printed":""}'
    ),

    "java": (
        '{"results":[{"call":"assertEquals(1,a);","correct":true},{"call":"assertEquals(2,b);",'
        '"correct":true}],"solved":true,"printed":""}'
    ),

    "jsp": {
        "results": [
            {
                "call": "assertEquals(false,response.html().indexOf(\"Hello Pineapples\") == -1);",
                "correct": True
            },
            {
                "call": "assertEquals(false,response.html().indexOf(\"Today is: \"+expectedDate)==-1);",
                "correct": True
            },
            {
                "call": "assertEquals(false,response.html().indexOf(\"The request parameter 'fruit' has a value of guava\")==-1);",
                "correct": True
            },
            {
                "call": "assertEquals(\"embedded\",response.select(\"table tr td p b\").html());",
                "correct": True
            }
        ],
        "solved": True,
        "printed": ""
    },

    "js": (
        '{"results":[{"call":"assert_equal(1,a);","correct":true},{"call":"assert_equal(2,b);",'
        '"correct":true}],"solved":true}'
    )
}

JAVA_LIST = ["java","jsp","ruby","js"]

ALL_HUMAN_NAMES = {
    "r": "R",
     "c": "C",
     "oc": "Objetive C",
     "scipy": "Scipy",
     "python": "Python",
     "jsp": "JSP",
     "java": "Java",
     "ruby": "Ruby",
     "js": "JavaScript",
}

LAST_DISK_CHECK = 0

NODE_SERVER_URL = "http://localhost:3001"


def Command(*cmd, **kwargs):
    """Enables to run subprocess commands in a different thread with
    TIMEOUT option!

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    and  https://gist.github.com/1306188

    """
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


def SendToJava(verifier, jsonrequest):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect(("localhost", 2012))
    except BaseException:
        return {"error": "JavaServer is down please restart the instance"}

    message = verifier+" "*(10-len(verifier)) + jsonrequest
    message = base64.b64encode(message)

    count = len(message)
    msb, lsb = divmod(count, 256) # split to two bytes

    try:
        s.send(chr(msb))
        s.send(chr(lsb))
        s.send(message)
        data =  s.recv(102400)
        s.close()
    except BaseException:
        return {"error": "JavaServer is down please restart the instance"}

    response =  repr(data).decode('UTF-8')
    response = response[response.index("ey"):].strip("'")
    response = base64.b64decode(response)
    response = response[response.index("{"):].strip("'")
    if response.startswith("{{"):
        response = response[1:]
    return response


def sendToAngularVerifier(jsonrequest, timeout=5):
    """Send a test request to Angular Verifier

    """
    data = json.dumps({"jsonrequest": jsonrequest})
    req = urllib2.Request(NODE_SERVER_URL)
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib2.urlopen(req, data=data, timeout=timeout)
    except socket.timeout:
        return {
            "error": (
                "Your code took too long to return. Your solution may be stuck "
                "in an infinite loop. Please try again."
            )
        }
    except urllib2.URLError as e:
        return {
            "error": "Unexpected error (%s)." % str(e)
        }

    if resp.code >= 500:
        return {"error": "NodeServer is down. Please restart the instance"}
    else:
        return json.load(resp)


class CommitHandler(tornado.web.RequestHandler):

    def get(self):
        commit = os.popen("git rev-parse HEAD").read()
        mini_commit = commit[0:10]
        url = (
            "<a href='https://github.com/SingaporeClouds/scipy-verifier/commit/"
            + commit + "'>" + mini_commit + "</a>"
        )
        self.set_header("Content-type","text/html")
        self.write("Commit : " + url)
        self.finish()


class VerifierHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, verifierName):
        Thread(target=self.delete_old_files, args=()).start()
        Thread(target=self.verifier, args=("GET", verifierName)).start()

    @tornado.web.asynchronous
    def post(self, verifierName):
        Thread(target=self.delete_old_files, args=()).start()
        Thread(target=self.verifier, args=("POST", verifierName)).start()


    def delete_old_files(self):
        global LAST_DISK_CHECK

        paths = [
            "/var/local/singpath_verifier/unity/out",
             "/var/local/singpath_verifier/unity/test",
             "/tmp",
             "/var/local/singpath_verifier/javaserver/jsp/tomcat/webapps/ROOT/"
        ]

        now = time.time()
        if now - LAST_DISK_CHECK > 60*60:
            remove_old_file(LAST_DISK_CHECK, paths)
            LAST_DISK_CHECK = now

    def verifier(self, method, verifierName=None):

        run = True
        if not verifierName in VERIFIERS_DICT:
            result = {'errors': 'verifier not exist'}
            logging.error("verifier not found")
            run = False
        else:
            jsonrequest = self.get_argument("jsonrequest", None)
            if jsonrequest != None:
                if method == "GET":
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
            #tell to verifier that only you want to run a code without test
            only_play = self.get_argument("only_play", "0")
            if only_play != "0":
                only_play = "1"
            if verifierName in JAVA_LIST:
                try:
                    result = SendToJava(verifierName, jsonrequest)
                except BaseException:
                    result = json.dumps(
                        {
                            "errors": (
                                "Very strange error please talk with the programmer"
                            )
                        }
                    )
                if  vcallback is not None:
                    result = vcallback + "(" + result + ")"
                self.set_header("Content-type", "text/plain")
                self.write(result)
                self.finish()
                return
            elif verifierName == "angular":
                result = sendToAngularVerifier(jsonrequest)
            else:
                try:
                    result = json.loads(
                        Command(
                            "/usr/bin/env",
                            "python",
                            FOLDER + "/verifiers/%s" % VERIFIERS_DICT[verifierName],
                            jsonrequest,
                            only_play,
                            timeout=5
                        )
                    )
                except Empty:
                    s = (
                        "Your code took too long to return. Your solution may be stuck "
                        "in an infinite loop. Please try again."
                    )
                    result = {"errors": s}
                    logging.error(s)

        result = json.dumps(result)

        if  vcallback is not None:
            result = vcallback + "(" + result + ")"

        self.set_header("Content-type", "text/plain")
        self.write(result)
        self.finish()


class BasicHealthCheckHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        Thread(target=self.check_all_but_r, args=()).start()

    def check_all_but_r(self):
        self.check(exception_list=["r"])

    def check(self, exception_list=[]):
        Fail = False
        verifiers_status = {}

        for i in PYTHON_TESTS:
            if i in exception_list:
                continue
            try:
                result = json.loads(
                    Command(
                        "/usr/bin/env",
                        "python",
                        FOLDER + "/verifiers/%s" % VERIFIERS_DICT[i],
                        json.dumps(PYTHON_TESTS[i]),
                        '0',
                        timeout=5
                    )
                )
            except Empty:
                s = (
                    "Your code took too long to return. Your solution may be stuck "
                    "in an infinite loop. Please try again."
                )
                result = {"errors": s}

            if PYTHON_RESULTS[i] == result:
                verifiers_status[i] = "<font style='color:green;font-weight:bold;'>OK</font>"
            else:
                verifiers_status[i] = "<font style='color:red;font-weight:bold;'>Fail</font>"
                Fail = True

        for i in JAVA_TESTS:
            if i in exception_list:
                continue
            try:
                result = SendToJava(i, json.dumps(JAVA_TESTS[i]))
            except BaseException:
                result = json.dumps({"errors": "Very strange error please talk with the dev"})

            if i=="jsp":
                 verifiers_status[i] = "<span style='color:green;span-weight:bold;'>OK</span>"
            else:
                if JAVA_RESULTS[i] == result:
                    verifiers_status[i] = "<span style='color:green;span-weight:bold;'>OK</span>"
                else:
                    verifiers_status[i] = "<span style='color:reed;span-weight:bold;'>Fail</span>"
                    Fail = True

        human_names= dict((k,v,) for k, v in ALL_HUMAN_NAMES.items() if k not in exception_list)
        html = """{% autoescape None%}<html>
        <body>
        <table>
        <thead>
            <tr><th>verifier</th><th>is running?</th></tr>
        </thead>
        <tbody>
        {% for i in human_names %}
            <tr><td>{{human_names[i]}}</td><td>{{verifiers_status[i]}}</td></tr>
        {% end %}
        </tbody>
        </table>
        </body>
        </html>"""
        t = tornado.web.template.Template(html)
        self.write(t.generate(human_names=human_names,verifiers_status=verifiers_status))
        if Fail:
            self._status_code = 500

        self.finish()


class HealthCheckHandler(BasicHealthCheckHandler):

    @tornado.web.asynchronous
    def get(self):
        Thread(target=self.check, args=()).start()


application = tornado.web.Application([
    (r"/", tornado.web.RedirectHandler, {"url": "/test/index.html"}),
    (r"^/current/commit$", CommitHandler),
    (r"^/test/(.*)", tornado.web.StaticFileHandler, {"path": "./python_server/testers"}),
    (r"^/([a-zA-Z0-9_]+)", VerifierHandler),
    (r"^/aws/health_check", HealthCheckHandler),
    (r"^/aws/basic_health_check", BasicHealthCheckHandler),
])


if __name__ == "__main__":
    #sys.stderr = open(FOLDER+"/error_log","a")
    #sys.stdout = open(FOLDER+"/log","a")

    application.listen(80)
    print 'Serving on 80...'
    tornado.ioloop.IOLoop.instance().start()
