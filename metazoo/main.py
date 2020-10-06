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
    if not ant.install():
        print('[FAILURE] Cleaning requires Ant!')
        return False
    print('Cleaning...')
    return os.system('cd {0} && bash {1} clean > /dev/null 2>&1'.format(loc.get_zookeeper_dir(), loc.get_ant_loc_bin())) == 0


def compile():
    print('Compiling...', flush=True)
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

    statuscode = os.system('cd {0} && bash {1} jar > /dev/null 2>&1'.format(zookeeper_loc, loc.get_ant_loc_bin()))

    if statuscode == 0:
        print('Compilation completed!')
    return statuscode == 0


def _exec_internal():
    return rmt.run()


def exec(force_comp=False, override_conf=False):
    print('Connected!', flush=True)
    if (force_comp or not is_compiled()):
        if not compile():
            print('[FAILURE] Could not compile!')
            return False
    elif is_compiled():
        print('Skipping compilation: Already compiled!')

    if override_conf:
        fs.rm(fs.join(loc.get_metazoo_config_dir(), 'metazoo.cfg'))
    psr.check_config() # Check configuration file and ask questions is necessary
    num_nodes_total = psr.get_num_nodes()

    command = 'prun -np {0} -1 python3 {1} --exec_internal'.format(num_nodes_total, fs.join(fs.abspath(), 'main.py'))
    print('Booting network...', flush=True)
    return os.system(command) == 0


def export(full_exp=False):
    print('Copying files using "{}" strategy...'.format('full' if full_exp else 'fast'))
    if full_exp:
        command = 'rsync -az {0} {1}:{2} {3} {4}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude .git',
            '--exclude __pycache__')
        if not clean():
            print('[FAILURE] Cleaning failed')
            return False
    else:
        print('[Note] This means we skip zookeeper-release-3.3.0 files.')
        command = 'rsync -az {0} {1}:{2} {3} {4} {5} {6}'.format(
            fs.dirname(fs.abspath()),
            rmt.get_remote(),
            loc.get_remote_dir(),
            '--exclude zookeeper-release-3.3.0',
            '--exclude deps',
            '--exclude .git',
            '--exclude __pycache__')

    return os.system(command) == 0


def _init_internal():
    print('Connected!', flush=True)
    if not compile():
        print('[FAILURE] Could not compile code on DAS5!')
        return False
    return True


def init():
    print('''
NOTICE: MetaZoo uses SSH to communicate with the DAS5.
In order to have a smooth experience, Install a SSH-key
to the DAS5 without password protection.
This way, you will not be asked for your password at every command.
''')
    print('Initializing MetaZoo...')
    if not export(full_exp=True):
        print('[FAILURE] Unable to export to DAS5 remote using user/ssh-key "{}"'.format(rmt.get_remote()))
        return False
    print('Connecting to {0}...'.format(rmt.get_remote()))

    tmp = os.system('ssh {0} "python3 {1}/zookeeper/metazoo/main.py --init_internal"'.format(rmt.get_remote(), loc.get_remote_dir())) == 0
    if tmp:
        print('[SUCCESS] Completed MetaZoo initialization. Use "{} --remote" to start execution on the remote host'.format(sys.argv[0]))


def remote(force_exp=False, force_comp=False, override_conf=False):
    if force_exp and not export(full_exp=True):
        print('[FAILURE] Could not export data')
        return False

    program = '--exec'+(' -c' if force_comp else '')+(' -o' if override_conf else '')

    command = 'ssh {0} "python3 {1}/zookeeper/metazoo/main.py {2}"'.format(
        rmt.get_remote(),
        loc.get_remote_dir(),
        program)
    print('Connecting to {0}...'.format(rmt.get_remote()))
    return os.system(command) == 0


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--clean', help='clean build directory', action='store_true')
    group.add_argument('--check', help='check whether environment has correct tools', action='store_true')
    group.add_argument('--compile', help='compile ancient', action='store_true')
    group.add_argument('--exec_internal', help=argparse.SUPPRESS, action='store_true')
    group.add_argument('--exec', help='call this on the DAS5 to handle server orchestration', action='store_true')
    group.add_argument('--export', help='export only metazoo and script code to the DAS5', action='store_true')
    group.add_argument('--init_internal', help=argparse.SUPPRESS, action='store_true')
    group.add_argument('--init', help='Initialize MetaZoo to run code on the DAS5', action='store_true')
    group.add_argument('--remote', help='execute code on the DAS5 from your local machine', action='store_true')
    parser.add_argument('-c', '--force-compile', dest='force_comp', help='Forces to (re)compile Zookeeper, even when build seems OK', action='store_true')
    parser.add_argument('-e', '--force-export', dest='force_exp', help='Forces to re-do the export phase', action='store_true')
    parser.add_argument('-o', '--override-conf', dest='override_conf', help='Forces MetaZoo to ignore existing configs', action='store_true')
    args = parser.parse_args()


    if args.compile: 
        compile()
    elif args.check:
        check()
    elif args.clean:
        clean()
    elif args.exec_internal:
        _exec_internal()
    elif args.exec:
        exec(force_comp=args.force_comp, override_conf=args.override_conf)
    elif args.export:
        export(full_exp=True)
    elif args.init_internal:
        _init_internal()
    elif args.init:
        init()
    elif args.remote:
        remote(force_exp=args.force_exp, force_comp=args.force_comp, override_conf=args.override_conf)
    

    if len(sys.argv) == 1:
        parser.print_help()

if __name__ == '__main__':
    main()