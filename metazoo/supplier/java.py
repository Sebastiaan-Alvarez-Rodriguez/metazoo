import os
import subprocess

def check_can_call(arglist):
    if len(arglist) > 0 and not subprocess.call(arglist, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0:
        print('Cannot call "{0}" for some reason. Please check if you have access permission to it.'.format(arglist[0]))
        return False
    return True

# Checks if given Java version is available on the system
def check_version(minVersion=8, maxVersion=8):
    returncode = True
    if not 'JAVA_HOME' in os.environ:
        print('JAVA_HOME is not set. Please set this environment variable to point to your Java installation directory.')
        returncode = False

    returncode &= check_can_call(['java', '-version'])
    returncode &= check_can_call(['javac', '-version'])

    java_version = subprocess.check_output('java -version 2>&1 | awk -F[\\\"_] \'NR==1{print $2}\'', shell=True).decode('utf-8').split('.')
    java_version_number = int(java_version[1])
    if java_version_number > maxVersion:
        print('Your Java version is too new. Please install Java version [{0}-{1}]. If you believe you have such version, use set_java.sh.'.format(minVersion, maxVersion))
        returncode = False
    elif java_version_number < minVersion:
        print('Your Java version is too old. Please install Java version [{0}-{1}]. If you believe you have such version, use set_java.sh'.format(minVersion, maxVersion))
        returncode = False

    javac_version = subprocess.check_output('javac -version 2>&1 | awk -F\' \' \'{print $2}\'', shell=True).decode('utf-8').split('.')
    tmp = int(javac_version[0])
    javac_version_number = tmp if tmp > 1 else int(javac_version[1])

    if javac_version_number > maxVersion:
        print('Your Javac version is too new. Please install Java version [{0}-{1}]. If you believe you have such version, use set_javac.sh.'.format(minVersion, maxVersion))
        returncode = False
    elif javac_version_number < minVersion:
        print('Your Javac version is too old. Please install Java version [{0}-{1}]. If you believe you have the right version, use set_javac.sh.'.format(minVersion, maxVersion))
        returncode = False

    return returncode