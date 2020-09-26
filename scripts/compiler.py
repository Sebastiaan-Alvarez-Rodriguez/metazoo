#!/usr/bin/python
import sys
import os
import subprocess

# Basic help function
def help():
    print('''
Ancient Zookeeper Compiler Helper (AZCH)

{0} <directive> [<directives>...]
Directives:
compile   Compile ancient Zookeeper
check     Check whether environment has correct tools
clean     Clean build directory
help      Display this useful information
''')
    return -1

def check_can_call(arglist):
    if len(arglist) > 0 and not subprocess.call(arglist, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0:
        print('Cannot call "{0}" for some reason. Please check if you have access permission to it.'.format(arglist[0]))
        return 1
    return 0

# Check if required tools (Apache Ant, Java8) are available
def check(print_success=True):
    returncode = 0
    if not 'JAVA_HOME' in os.environ:
        print('JAVA_HOME is not set. Please set this environment variable to point to your Java installation directory.')
        returncode = 1

    returncode &= check_can_call(['java', '-version'])
    returncode &= check_can_call(['javac', '-version'])
    returncode &= check_can_call(['ant', '-version'])


    java_version = subprocess.check_output('java -version 2>&1 | awk -F[\\\"_] \'NR==1{print $2}\'', shell=True).decode('utf-8').split('.')
    java_version_number = int(java_version[1])
    if java_version_number > 8:
        print('Your Java version is too new to compile with. Please install Java version [5-8]. If you believe you have such version, use set_java.sh.')
        returncode = 1
    elif java_version_number < 5:
        print('Your Java version is too old to compile with. Please install Java version [5-8]. If you believe you have such version, use set_java.sh')
        returncode = 1

    javac_version = subprocess.check_output('javac -version 2>&1 | awk -F\' \' \'{print $2}\'', shell=True).decode('utf-8').split('.')
    tmp = int(javac_version[0])
    javac_version_number = tmp if tmp > 1 else int(javac_version[1])

    if javac_version_number > 8:
        print('Your Javac version is too new to compile with. Please install Java version [5-8]. If you believe you have such version, use set_javac.sh.')
        returncode = 1
    elif javac_version_number < 5:
        print('Your Javac version is too old to compile with. Please install Java version [5-8]. If you believe you have the right version, use set_javac.sh.')
        returncode = 1

    if print_success and returncode == 0:
        print('[SUCCESS] Checks passed!')
    return returncode
# ant -version 2>&1 | awk -F' '  'NR==1{print$4}'


def compile():
    print('Compiling...')
    if check(print_success=False) != 0:
        print('[FAILURE] Cannot compile due to system errors')
        return 1
    if not os.path.isdir('zookeeper-release-3.3.0'):
        print('[FAILURE] Could not find {0}/zookeeper-release-3.3.0/'.format(os.getcwd()))
        return 1

    statuscode = os.system('cd ../zookeeper-release-3.3.0 && ant binary && cd ..')

    if statuscode == 0:
        print('[SUCCESS] Done!')
    return statuscode

def clean():
    print('Cleaning...')
    return os.system('cd ../zookeeper-release-3.3.0 && ant clean')

def main():
    if len(sys.argv) == 1:
        help()
    returncode = 0
    for arg in sys.argv[1:]:
        directive = arg.strip().lower()
        try:
            method = getattr(sys.modules[__name__], directive)
            returncode &= method()
        except AttributeError as e:
            print(e)
            print('Error: directive "{0}" not found'.format(directive))
    exit(returncode)
main()