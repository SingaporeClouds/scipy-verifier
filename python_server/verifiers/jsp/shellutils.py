import subprocess
import datetime
import os
import formatutils
import re
from shutil import copy

commands = { 
           'compile': '/usr/bin/c99 %s -o %s `gnustep-config --objc-flags` -lgnustep-base',
           'run': '%s',
           'compilejava': '/usr/bin/javac %s -cp %s/java/lib/junit-4.8.2.jar:%s',
           'runjava': '/usr/bin/java -cp %s/java/lib/junit-4.8.2.jar:%s %s',
           'compilejsp': '/usr/bin/javac %s -cp %s/java/lib/*:%s',
           'runjsp': '/usr/bin/java -cp %s/java/lib/*:%s %s %s' # note the extra %s at the end, which should be the name of the JSP 
           }

BASE_PATH = '/tmp'

def exec_command_and_get_output(cmd):
    cmd_array = ['/bin/bash', '-c', "(%s ; true)" % cmd]
    child = subprocess.Popen(cmd_array, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=BASE_PATH)
    s = child.communicate()[0]
    return s

def compile_java_and_get_results(code):
    global commands    
    
    # construct names for the source file and the compiled output
    now = datetime.datetime.now()
    uid = '%s_%06d' % (now.strftime('%Y%m%d_%H%M%S'), now.microsecond)
    base_name = 'JavaSolution_%s' % uid
    src_path = '%s/%s.java' % (BASE_PATH, base_name)
    binary_path = '%s/%s.class' % (BASE_PATH, base_name)
    curr_path = os.getcwd().replace(' ', '\\ ') # to get an absolute path to the junit JAR
    
    # Special requirement for java - because java requires that the public class name
    # must match the source file name, we do a quick search and replace
    code = re.sub('public class [a-zA-Z0-9_]*', 'public class %s' % base_name, code)
    
    # write out the source file based on the code passed in
    # also remove any already-compiled files if they exist
    f = open(src_path, 'w')
    f.write(code)
    f.close()
    if os.path.exists(binary_path): os.remove(binary_path)
    
    # compile and get the compile result
    compileResult = exec_command_and_get_output(commands['compilejava'] % (src_path, curr_path, BASE_PATH))
    
    # format the result into something more useable
    compile_warnings_and_errors = compileResult
    compile_errors = compileResult
    
    # make compileResult a dict containing both text outputs
    compileResult = {
        'warnings_and_errors': compile_warnings_and_errors,
        'errors': compile_errors
    }
    
    # if compilation is successful, run and get the result
    if os.path.exists(binary_path):
        result = exec_command_and_get_output(commands['runjava'] % (curr_path, BASE_PATH, base_name))
    else:
        result = ''
    
    return compileResult, result

# different from Java, requires both the testing code and the JSP code
def compile_jsp_and_get_results(code, jspcode):
    global commands
    
    # construct names for the source file and the compiled output
    now = datetime.datetime.now()
    uid = '%s_%06d' % (now.strftime('%Y%m%d_%H%M%S'), now.microsecond)
    base_name = 'JSPTest_%s' % uid
    src_java_path = '%s/%s.java' % (BASE_PATH, base_name)
    src_jsp_path = '%s/%s.jsp' % (BASE_PATH, base_name)
    binary_path = '%s/%s.class' % (BASE_PATH, base_name)
    curr_path = os.getcwd().replace(' ', '\\ ') # to get an absolute path to the junit JAR
    
    # Special requirement for java - because java requires that the public class name
    # must match the source file name, we do a quick search and replace
    # code = re.sub('public abstract class [a-zA-Z0-9_]*', 'public abstract class %s' % base_name, code)
    code = re.sub('JSPTester', base_name, code)
    
    # write out the Java source file
    f = open(src_java_path, 'w')
    f.write(code)
    f.close()
    if os.path.exists(binary_path): os.remove(binary_path)
    
    # write out the JSP source file
    f = open(src_jsp_path, 'w')
    f.write(jspcode)
    f.close()
    
    # copy log4j.properties if it doesn't exist    
    if not os.path.exists('%s/%s' % ('log4j.properties', BASE_PATH)): copy('%s/java/log4j.properties' % os.getcwd(), BASE_PATH)
    
    # compile and get the compile result
    compileResult = exec_command_and_get_output(commands['compilejsp'] % (src_java_path, curr_path, BASE_PATH))
    
    # format the result into something more useable
    compile_warnings_and_errors = compileResult
    compile_errors = compileResult
    
    # make compileResult a dict containing both text outputs
    compileResult = {
        'warnings_and_errors': compile_warnings_and_errors,
        'errors': compile_errors
    }
    
    # if compilation is successful, run and get the result againt the earlier saved JSP source file
    if os.path.exists(binary_path):
        result = exec_command_and_get_output(commands['runjsp'] % (curr_path, BASE_PATH, base_name, src_jsp_path))
        result = formatutils.parse_unit_test_results(result)
    else:
        result = None
        
    # store the commands that were executed
    compileResult['javac-command'] =  commands['compilejsp'] % (src_java_path, curr_path, BASE_PATH)
    compileResult['java-command'] = commands['runjsp'] % (curr_path, BASE_PATH, base_name, src_jsp_path)
    
    return compileResult, result

    
    
