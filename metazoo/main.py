#!/usr/bin/python
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'src'))
import dynamic.experiment as exp
import remote.remote as rmt
import result.results as res
from settings.settings import settings_instance as st
import supplier.ant as ant
import supplier.java as jv
from util.executor import Executor
import util.location as loc
import util.fs as fs
import util.time as tm
import util.ui as ui

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
    else:
        print('Compilation failed!')
    return statuscode == 0


def _exec_internal_client(debug_mode=False):
    return rmt.run_client(debug_mode)

def _exec_internal_server(debug_mode=False):
    return rmt.run_server(debug_mode)


def exec(repeats, force_comp=False, debug_mode=False):
    print('Connected!', flush=True)
    if not fs.isdir(loc.get_remote_metazoo_dir()):
        print('[FAILURE] Missing project on remote. Did you run "{} --init"?'.format(sys.argv[0]))
        return False
    if (force_comp or not is_compiled()):
        if not compile():
            print('[FAILURE] Could not compile!')
            return False
    elif is_compiled():
        print('Skipping compilation: Already compiled!')

    time_to_reserve = ui.ask_time('How much time to reserve on the cluster for {} repeats?'.format(repeats))

    timestamp = tm.ask_timestamp()
    # Constructs result and log directories
    for x in range(repeats):
        fs.mkdir(loc.get_metazoo_results_dir(), timestamp, x) 
        fs.mkdir(loc.get_metazoo_results_dir(), timestamp, x, 'experiment_logs')

    print('Loading experiment...', flush=True)
    experiment = exp.get_experiment(timestamp)

    experiment.pre_experiment(repeats)

    # Remove stale dirs from previous runs
    fs.rm(loc.get_remote_crawlspace_dir(), ignore_errors=True)
    fs.mkdir(loc.get_remote_crawlspace_dir())
    fs.rm(loc.get_cfg_dir(), '.metazoo.cfg', ignore_errors=True)

    # Build commands to boot the experiment
    aff_server = experiment.servers_core_affinity
    nodes_server = experiment.num_servers // aff_server
    command_server = 'prun -np {} -{} -t {} python3 {} --exec_internal_server {}'.format(nodes_server, aff_server, time_to_reserve, fs.join(fs.abspath(), 'main.py'), '-d' if debug_mode else '')
    aff_client = experiment.clients_core_affinity
    nodes_client = experiment.num_clients // aff_client
    command_client = 'prun -np {} -{} -t {} python3 {} --exec_internal_client {}'.format(nodes_client, aff_client, time_to_reserve, fs.join(fs.abspath(), 'main.py'), '-d' if debug_mode else '')

    print('Booting network...', flush=True)
    server_exec = Executor(command_server)
    client_exec = Executor(command_client)

    Executor.run_all(server_exec, client_exec, shell=True)
    status = Executor.wait_all(server_exec, client_exec)

    experiment.post_experiment()
    experiment.clean()

    if status:
        print('[SUCCESS] Experiment complete!')
    else:
        print('[FAILURE] Experiment had errors!')
    return status


def export(full_exp=False):
    print('Copying files using "{}" strategy, using key "{}"...'.format('full' if full_exp else 'fast', st.ssh_key_name))
    if full_exp:
        command = 'rsync -az {} {}:{} {} {} {}'.format(
            fs.dirname(fs.abspath()),
            st.ssh_key_name,
            loc.get_remote_metazoo_parent_dir(),
            '--exclude .git',
            '--exclude __pycache__',
            '--exclude zookeeper-client')
        if not clean():
            print('[FAILURE] Cleaning failed')
            return False
    else:
        print('[Note] This means we skip zookeeper-release-3.3.0 files.')
        command = 'rsync -az {} {}:{} {} {} {} {} {}'.format(
            fs.dirname(fs.abspath()),
            st.ssh_key_name,
            loc.get_remote_parent_dir(),
            '--exclude zookeeper-release-3.3.0',
            '--exclude zookeeper-client',
            '--exclude deps',
            '--exclude .git',
            '--exclude __pycache__')
    if os.system(command) == 0:
        print('Export success!')
        return True
    else:
        print('Export failure!')
        return False    


def _init_internal():
    print('Connected!', flush=True)
    if not compile():
        print('[FAILURE] Could not compile code on DAS5!')
        exit(1)
    exit(0)


def init():
    print('Initializing MetaZoo...')
    if not export(full_exp=True):
        print('[FAILURE] Unable to export to DAS5 remote using user/ssh-key "{}"'.format(st.ssh_key_name))
        return False
    print('Connecting using key "{0}"...'.format(st.ssh_key_name))

    tmp = os.system('ssh {0} "python3 {1}/metazoo/main.py --init_internal"'.format(st.ssh_key_name, loc.get_remote_metazoo_dir())) == 0
    if tmp:
        print('[SUCCESS] Completed MetaZoo initialization. Use "{} --remote" to start execution on the remote host'.format(sys.argv[0]))


def remote(repeats, force_exp=False, force_comp=False, debug_mode=False):
    if force_exp and not export(full_exp=True):
        print('[FAILURE] Could not export data')
        return False

    program = '--exec {}'.format(repeats)
    program +=(' -c' if force_comp else '')+(' -d' if debug_mode else '')


    command = 'ssh {0} "python3 {1}/metazoo/main.py {2}"'.format(
        st.ssh_key_name,
        loc.get_remote_metazoo_dir(),
        program)
    print('Connecting using key "{0}"...'.format(st.ssh_key_name))
    return os.system(command) == 0

def settings():
    st.change_settings()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    subparser = parser.add_subparsers()
    res.subparser(subparser)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--clean', help='clean build directory', action='store_true')
    group.add_argument('--check', help='check whether environment has correct tools', action='store_true')
    group.add_argument('--compile', help='compile ancient', action='store_true')
    group.add_argument('--exec_internal_client', help=argparse.SUPPRESS, action='store_true')
    group.add_argument('--exec_internal_server', help=argparse.SUPPRESS, action='store_true')
    group.add_argument('--exec', nargs=1, metavar='repeats', help='call this on the DAS5 to handle server orchestration')
    group.add_argument('--export', help='export only metazoo and script code to the DAS5', action='store_true')
    group.add_argument('--init_internal', help=argparse.SUPPRESS, action='store_true')
    group.add_argument('--init', help='Initialize MetaZoo to run code on the DAS5', action='store_true')
    group.add_argument('--remote', nargs=1, metavar='repeats', help='execute code on the DAS5 from your local machine')
    # group.add_argument('--results', nargs='+', help='Process results on local machine')
    group.add_argument('--settings', help='Change settings', action='store_true')
    parser.add_argument('-c', '--force-compile', dest='force_comp', help='Forces to (re)compile Zookeeper, even when build seems OK', action='store_true')
    parser.add_argument('-d', '--debug-mode', dest='debug_mode', help='Run remote in debug mode', action='store_true')
    parser.add_argument('-e', '--force-export', dest='force_exp', help='Forces to re-do the export phase', action='store_true')
    args = parser.parse_args()

    if res.result_args_set(args):
        res.results(parser, args)
    elif args.compile: 
        compile()
    elif args.check:
        check()
    elif args.clean:
        clean()
    elif args.exec_internal_client:
        _exec_internal_client(args.debug_mode)
    elif args.exec_internal_server:
        _exec_internal_server(args.debug_mode)
    elif args.exec:
        exec(int(args.exec[0]), force_comp=args.force_comp, debug_mode=args.debug_mode)
    elif args.export:
        export(full_exp=True)
    elif args.init_internal:
        _init_internal()
    elif args.init:
        init()
    elif args.remote:
        remote(int(args.remote[0]), force_exp=args.force_exp, force_comp=args.force_comp, debug_mode=args.debug_mode)
    elif args.settings:
        settings()

    if len(sys.argv) == 1:
        parser.print_help()

if __name__ == '__main__':
    main()