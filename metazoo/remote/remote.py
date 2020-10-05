# Code in this file is executed on each server.
# The goal is to boot a zookeeper server, and make sure it knows of the other ones

import os
import socket
import time

import util.fs as fs
import util.location as loc
from remote.executor import Executor
from remote.config import Config

def get_remote():
    return 'dpsdas5LU'

# Generates the Zookeeper config file, and returns our unique identifier
def generate_config():
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()

    port_to_leader = 2182
    port_to_elect  = 2183 # Note: This port is not needed if electionAlg=0 (default alg=3)
    
    # This list should be the same everywhere
    # TODO: Use infiniband connection
    serverlist = ['server.{0}=node{1}:{2}:{3}'.format(idx+1, nodenumber, port_to_leader, port_to_elect) for idx, nodenumber in enumerate(nodenumbers)]

    # The server id is unique
    server_id  = nodenumbers.index(int(socket.gethostname()[4:]))+1
    ticktime   = 2000
    initlimit  = 10
    synclimit  = 5
    datadir    = '{0}/crawlspace/mahadev/zookeeper/server{1}/data'.format(loc.get_remote_dir(), server_id)
    clientport = 2181

    config_string = '''
tickTime={0}
initLimit={1}
syncLimit={2}
dataDir={3}
clientPort={4}
{5}'''.format(
    ticktime,
    initlimit,
    synclimit,
    datadir,
    clientport,
    '\n'.join(serverlist))

    with open(fs.join(loc.get_cfg_dir(), '{}.cfg'.format(server_id)), 'w') as file:
        file.write(config_string)
    return Config(server_id, datadir)


# Starts Zookeeper, returns immediately after starting a thread containing our process
def boot_zookeeper(config):
    # return os.system('bash {0} start &'.format(fs.join(get_remote_bin_dir(), 'zkServer.sh'))) == 0

    classpath = os.environ['CLASSPATH'] if 'CLASSPATH' in os.environ else ''
    prefix = ':'.join([
        loc.get_cfg_dir(),
        ':'.join([file for file in fs.ls(loc.get_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        ':'.join([file for file in fs.ls(loc.get_build_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        fs.join(loc.get_build_dir(), 'classes')])

    log4j_loc = '.'
    log4j_properties = 'ERROR,CONSOLE' # Log INFO-level information, send to console

    classpath = '{}:{}'.format(prefix, classpath)
    zoo_main = '-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.local.only=false org.apache.zookeeper.server.quorum.QuorumPeerMain'
    conf_location = fs.join(loc.get_cfg_dir(), str(config.server_id)+'.cfg')

    command = 'java "-Dzookeeper.log.dir={}" "-Dzookeeper.root.logger={}" -cp "{}" {} "{}" > /dev/null 2>&1'.format(log4j_loc, log4j_properties, classpath, zoo_main, conf_location)
    executor = Executor(command)
    executor.run(shell=True)

    fs.mkdir(config.datadir, exist_ok=True)
    with open(fs.join(config.datadir, 'myid'), 'w') as file: #Write myid file
        file.write(str(config.server_id))
    return executor


def status_zookeeper():
    return os.system('bash {0} status'.format(fs.join(loc.get_bin_dir(), 'zkServer.sh'))) == 0


# Stops Zookeeper, returns immediately
def stop_zookeeper(executor, config):
    tmp = executor.stop()
    fs.rm(config.datadir, 'myid') # Remove myid file
    return tmp


def run():
    config = generate_config()
    print('-----------------[ Going to boot    ({}) ]-----------------'.format(config.server_id), flush=True)
    executor = boot_zookeeper(config)
    print('-----------------[ Boot complete    ({}) ]-----------------'.format(config.server_id), flush=True)
    time.sleep(10)
    # status_zookeeper()
    print('-----------------[ Going to halt    ({}) ]-----------------'.format(config.server_id), flush=True)
    stop_zookeeper(executor, config)
    print('-----------------[ Halting complete ({}) ]-----------------'.format(config.server_id), flush=True)
    return True