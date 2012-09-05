import re
import logging

types = [
    {'call': 'AssertEquals'},
    {'call': 'AssertEqualObjects'},
]

# any line of code that is a test command
RE_TEST_COMMAND = re.compile("\s*(page|element|assert|onRequest)")
RE_CALL_LINE = re.compile("\s*call: (.*)")
RE_CORRECT_LINE = re.compile("\s*correct: (.*)")
RE_EXPECTED_LINE = re.compile("\s*expected: (.*)")
RE_RECEIVED_LINE = re.compile("\s*received: (.*)")

def correct_line_numbers(string, src_file):
    result = ''
    for line in string.split('\n'):
        mo = re.compile('^(.*%s:)([0-9]+)(:.*)$' % src_file).search(line)
        if mo:
            lineno = int(mo.group(2)) - 3
            line = '%s%s%s' % (mo.group(1), lineno, mo.group(3))
        if result:
            result += '\n'
        result += '%s' % line
    return result

'''Takes lines of assertions and wraps them in try {} catch {}, which will
allow assertions to continue even on failures'''
def wrapAssertions(string):
    wrappedAssertions = ''
    for line in string.split('\n'):
        if not (RE_TEST_COMMAND.match(line) is None):
            call = line.replace('"', '\\"')            
            line = 'try { beginTest(); %s } catch (Error e) { setErrorMsg(e.getMessage()); } finally { formatTestResult("%s"); }' % (line, call)
        wrappedAssertions += str(line) + '\n'
        
    return wrappedAssertions

'''Transforms unit test results, which should come in groups of 4 lines, into a dict'''
def parse_unit_test_results(rawoutput):
    jsonObj = {}    
    results = []
    solved = True
    others = []
    
    # init the currentresult and iterate through each line
    currentresult = {}
    for line in rawoutput.split('\n'):
        if RE_CALL_LINE.match(line):
            currentresult['line'] = str(RE_CALL_LINE.search(line).group(1))
        elif RE_CORRECT_LINE.match(line):
            currentresult['correct'] = RE_CORRECT_LINE.search(line).group(1) == 'true'
            if not currentresult['correct']: solved = False
        elif RE_EXPECTED_LINE.match(line):
            currentresult['expected'] = RE_EXPECTED_LINE.search(line).group(1)
        elif RE_RECEIVED_LINE.match(line):
            # this is the last line
            currentresult['received'] = RE_RECEIVED_LINE.search(line).group(1)
            results.append(currentresult)
            currentresult = {}
        else:
            others.append(line)
    
    # we are done
    jsonObj['results'] = results
    jsonObj['solved'] = solved
    jsonObj['others'] = others
    return jsonObj
    
def grep(string, pattern):
    matches = ''
    for line in string.split('\n'):
        match = (pattern in line)
        if not match:
            try:
                match = True if re.compile(pattern).search(line) else False
            except:
                pass
        if match:
            matches += str(line) + '\n'
    return matches

def format_tests(tests, solution):
    global types
    res = ''
    resultList = []
    testCases = tests.splitlines()
    line_number = 11 + len(solution.splitlines()) #the first test line
    for testCase in testCases:
        testCase = testCase.strip()
        type = None
        if not testCase.startswith('//'):
            for t in types:
                if t['call'] in testCase:
                    type = t
                    break
        if type:
            exp = '([^,]+)'
            parse_exp = '%s\(%s *, *%s\);' % (type['call'], exp, exp)
            mo = re.compile(parse_exp).search(testCase)
            if mo:
                call = mo.group(1)
                expected = mo.group(2)
                resultList.append({
                    'call': call,
                    'expected': expected,
                    'received': expected,
                    'correct': None,
                    'line': line_number,
                    'type': type
                    })
                res += '%s(%s, %s);\n' % (type['call'], call, expected)
            else:
                res += '%s\n' % testCase
        else:
            res += '%s\n' % testCase
        line_number += 1
    logging.info('res:\n%s\nresultList: %s' % (res, resultList))
    return res, resultList

def render_template(path, variables):
    f = open(path, 'r')
    template = f.read()
    return template % variables
