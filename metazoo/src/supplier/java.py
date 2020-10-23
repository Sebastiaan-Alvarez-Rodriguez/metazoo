# In this file, we provide functions to interact with Java
# We explicitly do NOT provide ways to install Java,
# as it is already installed on the DAS5

import os
import subprocess

import util.fs as fs
from util.printer import *
import util.ui as ui

# Check if we can call given arguments. Returns True if we can, False otherwise
def check_can_call(arglist):
    if len(arglist) > 0 and not subprocess.call(arglist, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0:
        print('Cannot call "{0}" for some reason. Please check if you have access permission to it.'.format(arglist[0]))
        return False
    return True

'''
Attempt to set the JAVA_HOME in the user's .bashrc file.
We ask permission before modifying the .bashrc.

Return True if a valid JAVA_HOME is set, False otherwise
'''
def resolve_JAVA_HOME():
    java_bin = subprocess.check_output('which java', shell=True).decode('utf-8').strip()
    if fs.issymlink(java_bin):
        java_bin = fs.resolvelink(java_bin)

    if fs.dirname(fs.dirname(java_bin)).endswith('jre'):
        java_bin = fs.join(fs.dirname(fs.dirname(fs.dirname(java_bin))), 'bin')
    
    if not 'javac' in fs.ls(java_bin, only_files=True):
        printe('Could not find valid JAVA_HOME.')
        return False

    target_location = fs.dirname(java_bin) #from <path>/bin/ to <path>
    print('Valid JAVA_HOME target found: {}'.format(target_location))
    if ui.ask_bool('Can I write this target location to your .bashrc?'):
        with open(fs.join(os.environ['HOME'], '.bashrc'), 'a') as file:
            file.write('export JAVA_HOME={}\n'.format(target_location))
            os.system('source ~/.bashrc')
            prints('JAVA_HOME set!')
            return True
    return False

# Checks if a Java installation within version bounds is available on the system
def check_version(minVersion=8, maxVersion=8):
    returncode = True
    if not 'JAVA_HOME' in os.environ:
        printw('JAVA_HOME is not set. Detecting automatically...')
        if not resolve_JAVA_HOME():
            printe('Unable to detect JAVA_HOME. Set JAVA_HOME yourself.')
            print('Note: Java is commonly installed in /usr/lib/jvm/...')
            returncode = False
    elif not fs.isfile(os.environ['JAVA_HOME'], 'bin', 'java'):
        printe('Incorrect JAVA_HOME set: Cannot reach JAVA_HOME/bin/java ({0}/bin/java'.format(os.environ['JAVA_HOME']))
        print('Note: Java is commonly installed in /usr/lib/jvm/...')
        returncode = False
    returncode &= check_can_call(['java', '-version'])
    returncode &= check_can_call(['javac', '-version'])

    java_version = subprocess.check_output('java -version 2>&1 | awk -F[\\\"_] \'NR==1{print $2}\'', shell=True).decode('utf-8').split('.')
    java_version_number = int(java_version[1])
    if java_version_number > maxVersion:
        printe('Your Java version is too new. Please install Java version [{0}-{1}]. If you believe you have such version, use set_java.sh.'.format(minVersion, maxVersion))
        returncode = False
    elif java_version_number < minVersion:
        printe('Your Java version is too old. Please install Java version [{0}-{1}]. If you believe you have such version, use set_java.sh'.format(minVersion, maxVersion))
        returncode = False

    javac_version = subprocess.check_output('javac -version 2>&1 | awk -F\' \' \'{print $2}\'', shell=True).decode('utf-8').split('.')
    tmp = int(javac_version[0])
    javac_version_number = tmp if tmp > 1 else int(javac_version[1])

    if javac_version_number > maxVersion:
        printe('Your Javac version is too new. Please install Java version [{0}-{1}]. If you believe you have such version, use set_javac.sh.'.format(minVersion, maxVersion))
        returncode = False
    elif javac_version_number < minVersion:
        printe('Your Javac version is too old. Please install Java version [{0}-{1}]. If you believe you have the right version, use set_javac.sh.'.format(minVersion, maxVersion))
        returncode = False

    return returncode