#!/usr/bin/python
import sys
import os
import subprocess

import util.fs as fs
import supplier.java as jv
import supplier.ant as ant


# Basic help function
def help():
    print('''
Meta Zookeeper

{0} <directive> [<directives>...]
Directives:
compile   Compile ancient Zookeeper
check     Check whether environment has correct tools
clean     Clean build directory
help      Display this useful information
'''.format(sys.argv[0]))
    return False

def get_zookeeper_loc():
    return fs.join(fs.dirname(fs.abspath()), 'zookeeper-release-3.3.0')

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


def compile():
    print('Compiling...')
    if not ant.install():
        print('[FAILURE] Cannot install Apache Ant')
        return False

    if not check(silent=True):
        print('[FAILURE] Cannot compile due to system errors')
        return False

    zookeeper_loc = get_zookeeper_loc()
    if not fs.isdir(zookeeper_loc):
        print('[FAILURE] Could not find {0}'.format(zookeeper_loc))
        return False

    statuscode = os.system('cd {0} && bash {1} binary'.format(zookeeper_loc, ant.get_ant_loc_bin()))

    if statuscode == 0:
        print('[SUCCESS] Done!')
    return statuscode == 0


def clean():
    if not ant.ant_available():
        print('Cleaning requires Ant!')
        return False
    print('Cleaning...')
    return os.system('cd {0} && bash {1} clean'.format(get_zookeeper_loc(), ant.get_ant_loc_bin())) == 0

def main():
    if len(sys.argv) == 1:
        help()
    returncode = 0
    for arg in sys.argv[1:]:
        directive = arg.strip().lower()
        try:
            method = getattr(sys.modules[__name__], directive)
            returncode &= 1 if method() else 0
        except AttributeError as e:
            print(e)
            print('Error: directive "{0}" not found'.format(directive))
    exit(returncode)
main()