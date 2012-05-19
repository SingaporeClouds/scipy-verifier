import json 
import logging
import re
import uuid
import os
import sys
import pwd
from Queue import Queue

def correct_line_numbers( string, src_file):
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
    
def runObjetiveCInstance(jsonrequest,outQueue):
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
    
    types = [
             {'call': 'AssertEquals'},
             {'call': 'AssertEqualObjects'}
             ]
    res = ''
    resultList = []
    testCases = tests.splitlines()
    line_number = 11 + len(solution.splitlines()) #the first test line
    for testCase in testCases:
        testCase = testCase.strip()
        _type = None
        if not testCase.startswith('//'):
            for t in types:
                if t['call'] in testCase:
                    _type = t
                    break
        if _type:
            exp = '([^,]+)'
            parse_exp = '%s\(%s *, *%s\);' % (_type['call'], exp, exp)
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
                res += '%s(%s, %s);\n' % (_type['call'], call, expected)
            else:
                res += '%s\n' % testCase
        else:
            res += '%s\n' % testCase
        line_number += 1
    logging.info('res:\n%s\nresultList: %s' % (res, resultList))
    formattedTests, resultList =  res, resultList
    #Update the objective C test file by pasting in the solution code and tests.
    code = \
            """#import <Foundation/Foundation.h>
               #import <stdio.h>

            %(solution)s
            void fjskdjhgkjhgskjghkjsdahlksdjh() {
            }
            
            //replaces all occurences with another occurence
            char *str_replace(char * orig, char * search, char * replace){
                if (!strstr(orig, search)) {
                    return orig;
                }
                char * pos = "\\0";
                char * buffer = malloc(strlen(orig) * 2);
                buffer[0] = '\\0';
                while (strstr(orig, search)) {
                    pos = strstr(orig, search);
                    strncpy(buffer + strlen(buffer), orig, pos - orig);
                    strcat(buffer, replace);
                    pos += strlen(search);
                    orig = pos;
            
                }
                return strcat(buffer, pos);
            }
            
            NSString * toString(NSValue *value) {
                if (strcmp([value objCType], "i") == 0) {
                    int valPtr;
                    [value getValue:&valPtr];
                    return [NSString stringWithFormat:@"%%i", valPtr];
                }
                if (strcmp([value objCType], "f") == 0) {
                    float valPtr;
                    [value getValue:&valPtr];
                    return [NSString stringWithFormat:@"%%g", valPtr];
                }
                if (strcmp([value objCType], "d") == 0) {
                    double valPtr;
                    [value getValue:&valPtr];
                    return [NSString stringWithFormat:@"%%g", valPtr];
                }
                if (strcmp([value objCType], "@") == 0) {
                    int valPtr;
                    [value getValue:&valPtr];
                    return [NSString stringWithFormat:@"\\\\\\"%%@\\\\\\"", valPtr];
                }
                void * valPtr;
                [value getValue:&valPtr];
                NSString * format = [NSString stringWithFormat:@"%%%%%%s", [value objCType]]; 
                return [NSString stringWithFormat:format, valPtr];
            }
            #define AssertEquals(a, b) \\
                do { \\
                    __typeof__(a) avalue = (a); \\
                    __typeof__(b) bvalue = (b); \\
                    NSValue *aencoded = [NSValue value:&avalue withObjCType: @encode(__typeof__(avalue))]; \\
                    NSValue *bencoded = [NSValue value:&bvalue withObjCType: @encode(__typeof__(bvalue))]; \\
                    int __result = 0; \\
                    if (@encode(__typeof__(avalue)) != @encode(__typeof__(bvalue))) { \\
                        __result = 0; \\
                    } else { \\
                        if ([aencoded isEqualToValue:bencoded]) { \\
                            __result = 1; \\
                        } \\
                    } \\
                    [results addObject:[NSArray arrayWithObjects: \\
                                    __result ? @"true" : @"false", \\
                                    [NSString stringWithFormat:@"%%@", toString(aencoded)], \\
                                    [NSString stringWithFormat:@"%%@", toString(bencoded)], \\
                                    [NSString stringWithFormat:@"AssertEquals(%%s, %%s);", str_replace(#a,"\\"", "\\\\\\""),\\
                                        str_replace(#b,"\\"", "\\\\\\"")], nil]]; \\
                } while(0);
            
            NSMutableArray * testMethod()
            {   
                //Paste the code under test here.
                //End of code under test
            NSMutableArray *results = [[NSMutableArray alloc] init];
                //Paste the tests in here
            %(tests)s
                //End of tests
                return results;
            }
            int main( int argc, const char *argv[] ) {
                NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
                NSMutableArray * results = testMethod();
            
                NSEnumerator *enumerator = [results objectEnumerator];
            
                printf("{\\"results\\": [");
                id row;
                int first = 1;
                int allSolved = 1;
                while ( (row = [enumerator nextObject]) ) {
                    NSString *correct = [row objectAtIndex:0];
                    NSString *expected = [row objectAtIndex:1];
                    NSString *received = [row objectAtIndex:2];
                    NSString *call = [row objectAtIndex:3];
            
                    if (allSolved && (strcmp([correct cString], "true") != 0)) {
                        allSolved = 0;
                    }
                    if (!first) printf(",");
                    else first = 0;
                    printf("{\\"expected\\": \\"%%s\\", \\"received\\": \\"%%s\\", \\"call\\": \\"%%s\\", \\"correct\\": %%s}",
                        [expected cString], [received cString], [call cString], [correct cString]);
                }
                printf("], \\"solved\\": %%s, \\"printed\\": \\"\\"}", (allSolved ? "true" : "false"));
            
                [pool release];
            
                return 0;
            }
            """ % {'solution': solution, 'tests': formattedTests}
    uid = uuid.uuid4()
    src_file = 'ObjCSolution_%s.m' % uid
    src_path = '/tmp/%s' % src_file
    binary_path = '/tmp/ObjCSolution_%s.out' % uid
    result_path = '/tmp/ObjCSolution_%s.result' % uid
    f = open(src_path, 'w')
    f.write(code)
    f.close()
    if os.path.exists(binary_path):
        os.remove(binary_path)
    #Execute the xcodebuild commandline options and read the results
    # xcodebuild -target Test
    cmd = 'gcc  %s -o %s `gnustep-config --objc-flags` -lgnustep-base' % ( src_path, binary_path)
        #cmd = ['/bin/bash', '-c', "%s ; true" % cmd]
    compileResult = os.popen(cmd).read()
    if os.path.exists(binary_path):
        cmd = ['/bin/bash', '-c', "%s ; true" % binary_path]
        result = os.popen(" ".join(cmd)).read()
    else:
        result = ''
    
    # Create a valid json respose based on the xcodebuild results or error returned.
    compile_warnings_and_errors = grep(compileResult, '%s:' % src_file)
    compile_warnings_and_errors = correct_line_numbers(compile_warnings_and_errors, src_file)
    compile_errors = grep(compileResult, '%s:[0-9]+: error:' % src_file)
    compile_errors = correct_line_numbers(compile_errors, src_file)
    if compile_errors:
        jsonResult = {'errors': compile_warnings_and_errors[0:450]}
    else:
        #it probably compiled, look for test results
        if result and result[0] == '{' and result[-1] == '}':
            jsonResult = json.loads(result)
        else: #other unecpected result
            s = '%s\n%s' % (compile_warnings_and_errors, result)
            jsonResult = {'errors': s[0:450]}
    s = json.dumps(jsonResult)
    if len(s) > 400:
        compile_warnings_and_errors = ''
    jsonResult['printed'] = compile_warnings_and_errors[0:450-len(s)]
    # Return the results
    s = json.dumps(jsonResult)
    out.put(s)
    
if __name__ == '__main__':
    pw_record      = pwd.getpwnam("verifiers")
    user_name      = pw_record.pw_name
    user_home_dir  = pw_record.pw_dir
    user_uid       = pw_record.pw_uid
    user_gid       = pw_record.pw_gid
    os.environ['HOME']     = user_home_dir
    os.environ['LOGNAME']  = user_name
    os.environ['USER']  = user_name
    os.environ['LANGUAGE']  = "en_US.UTF-8"
    os.environ['LANG']  = "en_US.UTF-8"
    os.environ['LC_ALL']  = "en_US.UTF-8"
    os.setgid(user_gid)
    os.setuid(user_uid)
    jsonrequet= sys.argv[1]
    out = Queue()
    runObjetiveCInstance(jsonrequet,out)
    print out.get()