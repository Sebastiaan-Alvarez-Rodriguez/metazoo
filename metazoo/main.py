#!/usr/bin/python
import sys
import os
import subprocess
import argparse

import util.location as loc
import util.fs as fs
import supplier.java as jv
import supplier.ant as ant
import remote.remote as rmt
import parse.parser as psr


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


def compile(slow=False):
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

    statuscode = os.system('cd {0} && bash {1} {2} > /dev/null 2>&1'.format(zookeeper_loc, loc.get_ant_loc_bin(), 'binary' if slow else 'jar'))

    if statuscode == 0:
        print('Compilation completed!')
    return statuscode == 0


def _exec_internal():
    return rmt.run()


def exec(slow=True, comp=True):
    print('Connected!', flush=True)
    if comp or not is_compiled():
        compile(slow=slow)
    elif is_compiled():
        print('Skipping compilation: Already compiled!')
    psr.check_config() # Check configuration file and ask questions is necessary

    command = 'prun -np {0} -1 python3 {1} --internal'.format(psr.get_num_nodes(), fs.join(fs.abspath(), 'main.py'))
    print('Booting network...', flush=True)
    return os.system(command) == 0


def export(slow=False):
    if slow:
        print('Copying files using normal strategy...')
        command = 'rsync -az {0} {1}:{2} {3}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude .git')
        if not clean():
            print('[FAILURE] Cleaning failed')
            return False
    else:
        print('Copying files using fast strategy...')
        command = 'rsync -az {0} {1}:{2} {3} {4} {5}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude zookeeper-release-3.3.0',
            '--exclude deps',
            '--exclude .git')

    return os.system(command) == 0


def remote(slow=False, exp=True, comp=True):
    if exp and not export(slow=slow):
        print('[FAILURE] Could not export data')
        return False

    program = '--exec'
    if slow:
        program += ' -s'
    if not comp:
        program += ' -c'

    command = 'ssh {0} "python3 {1}/zookeeper/metazoo/main.py {2}"'.format(
        rmt.get_remote(),
        loc.get_remote_dir(),
        program)
    print('Connecting to {0}...'.format(rmt.get_remote()))
    return os.system(command) == 0


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--compile', help='compile ancient', action='store_true')
    group.add_argument('--check', help='check whether environment has correct tools', action='store_true')
    group.add_argument('--clean', help='clean build directory', action='store_true')
    group.add_argument('--exec', help='call this on the DAS5 to handle server orchestration', action='store_true')
    group.add_argument('--export', help='export only metazoo and script code to the DAS5', action='store_true')
    group.add_argument('--remote', help='execute code on the DAS5 from your local machine', action='store_true')
    group.add_argument('--internal', help=argparse.SUPPRESS, action='store_true')
    parser.add_argument('-s', '--slow', help='''\
slow mode (only for compile, export, remote)
    compile: compile ancient Zookeeper fully, including src jars, javadoc etc
    export:  export all code to the DAS5, including zookeeper-release code and deps
    remote:  execute code on the DAS5 from your local machine, using normal export''', action='store_true')
    parser.add_argument('-c', '--no-compile', dest='skip_comp', help='skips the compilation phase (remote/ exec only)', action='store_true')
    parser.add_argument('-e', '--no-export', dest='skip_exp', help='skips the export phase (remote only)', action='store_true')
    args = parser.parse_args()


    if args.compile: 
        compile(slow=args.slow)
    elif args.check:
        check()
    elif args.clean:
        clean()
    elif args.exec:
        exec(slow=args.slow, comp=not args.skip_comp)
    elif args.export:
        export(slow=args.slow)
    elif args.remote:
        remote(slow=args.slow, exp=not args.skip_exp, comp=not args.skip_comp)
    elif args.internal:
        _exec_internal()
    

    if len(sys.argv) == 1:
        parser.print_help()

if __name__ == '__main__':
    main()