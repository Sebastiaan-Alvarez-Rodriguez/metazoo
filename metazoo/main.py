#!/usr/bin/python
import sys
import os
import subprocess

import util.location as loc
import util.fs as fs
import supplier.java as jv
import supplier.ant as ant
import remote.remote as rmt

def is_compiled():
    return fs.isfile(loc.get_build_dir(), 'zookeeper-3.3.0.jar')

# Basic help function
def help():
    print('''
Meta Zookeeper

{0} <directive> [<directives>...]
Directives:
compile_slow  Compile ancient Zookeeper fully, including src jars, javadoc etc
compile       Compile ancient
check         Check whether environment has correct tools
clean         Clean build directory
exec          Call this on the DAS5 to handle server orchestration
export_slow   Export all code to the DAS5, including zookeeper-release code and deps
export        Export only metazoo and script code to the DAS5
remote_slow   Execute code on the DAS5 from your local machine, using normal export
remote        Execute code on the DAS5 from your local machine
help          Display this useful information
'''.format(sys.argv[0]))


# Check if required tools (Apache Ant, Java8) are available
def check(silent=False):
    a = ant.ant_available()
    b = jv.check_version(minVersion=8, maxVersion=8)
    if a and b:
        if not silent:
            print('[SUCCESS] Requirements satisfied')
        return True
    if not silent:
        print('[FAILURE] Requirements not satisfied: ', end='')
        if not a:
            print('Ant', end='')
        if not b:
            print('Java 8', end='')
        print()
    return False


def clean():
    if not ant.ant_available():
        print('[FAILURE] Cleaning requires Ant!')
        return False
    print('Cleaning...')
    return os.system('cd {0} && bash {1} clean > /dev/null 2>&1'.format(loc.get_zookeeper_dir(), loc.get_ant_loc_bin())) == 0


def compile(fast=True):
    print('Compiling...')
    if not ant.install():
        print('[FAILURE] Cannot install Apache Ant')
        return False

    if not check(silent=True):
        print('[FAILURE] Cannot compile due to system errors')
        return False

    zookeeper_loc = loc.get_zookeeper_dir()
    if not fs.isdir(zookeeper_loc):
        print('[FAILURE] Could not find {0}'.format(zookeeper_loc))
        return False

    statuscode = os.system('cd {0} && bash {1} {2} > /dev/null 2>&1'.format(zookeeper_loc, loc.get_ant_loc_bin(), 'jar' if fast else 'binary'))

    if statuscode == 0:
        print('Compilation completed!')
    return statuscode == 0


def _exec_internal():
    rmt.run()


def exec(fast=True):
    print('Connected!')
    if fast and is_compiled():
        print('Skipping compilation: Already compiled!')
    else:
        compile(fast=True) # We do not want to build javadoc anyway
    try:
        nodes = input('How many nodes do you want to allocate? ').strip()
        nr_nodes = int(nodes)
    except Exception as e:
        print('[FAILURE] Input "{0}" is not a number'.format(nodes))
        return False

    command = 'prun -np {0} -1 python3 {1} _exec_internal'.format(nr_nodes, fs.join(fs.abspath(), 'main.py'))
    return os.system(command) == 0


def export(fast=True):
    if fast:
        print('Copying files using fast strategy...')
        command = 'rsync -az {0} {1}:{2} {3} {4} {5}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude zookeeper-release-3.3.0',
            '--exclude deps',
            '--exclude .git')
    else:
        print('Copying files using normal strategy...')
        command = 'rsync -az {0} {1}:{2} {3}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude .git')
        if not clean():
            print('[FAILURE] Cleaning failed')
            return False

    return os.system(command) == 0


def remote(fast=True):
    if not export(fast=fast):
        print('[FAILURE] Could not export data')
        return False

    command = 'ssh {0} "python3 {1}/zookeeper/metazoo/main.py {2}"'.format(
        rmt.get_remote(),
        loc.get_remote_dir(),
        'exec' if fast else 'exec_slow')
    print('Connecting to {0}...'.format(rmt.get_remote()))
    return os.system(command) == 0


def main():
    if len(sys.argv) == 1:
        help()
    returncode = 0


    for arg in sys.argv[1:]:
        directive = arg.strip().lower()
        try:
            # Fetch method to call
            method = getattr(sys.modules[__name__], directive)

            if not method():
                print('[FAILURE] Exception during directive {}'.format(arg))
        except AttributeError as e:
            if arg == 'compile_slow':
                compile(fast=False)
            elif arg == 'exec_slow':
                exec(fast=False)
            elif arg == 'export_slow':
                export(fast=False)
            elif arg == 'remote_slow':
                remote(fast=False)
            else:
                print(e)
                print('Error: directive "{0}" not found'.format(directive))
                exit(1)
    exit(returncode)

if __name__ == '__main__':
    main()