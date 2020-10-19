# Code in this file is executed on each server.
# The goal is to boot a zookeeper server, and make sure it knows of the other ones

import os

import util.fs as fs
import util.location as loc
from remote.config import ServerConfig
from remote.executor import Executor
import remote.identifier as idr


def nodenr_to_infiniband(nodenr):
    return '10.149.1.'+str(nodenr)[1:]



# Populates uninitialized config members
def populate_config(config):
    config.datadir   = '{0}/mahadev/zookeeper/server{1}/data'.format(loc.get_remote_crawlspace_dir(), config.gid)
    config.log4j_loc = loc.get_cfg_dir()
    config.log4j_properties = 'ERROR,CONSOLE' # Log ERROR-level information, send to console


# Generates the Zookeeper config file for this server instance.
# Config is written to zookeeper-release-3.3.0/conf/<serverid>.cfg
def gen_zookeeper_config(config):
    port_to_leader = 2182
    port_to_elect  = 2183
    
    # This list should be the same everywhere. End goal:
    # server.0=<ip1>:2182:2183 #share node1
    # server.1=<ip1>:2184:2185 #share node1
    # server.2=<ip2>:2182:2183 #share node2
    # server.3=<ip2>:2184:2185 #share node2
    # If we are server 1, then server.0 should have 'localhost' instead of <ip1>
    serverlist = []
    srv_id = 0
    for x in range(len(config.nodes) // idr.num_procs_per_node()):
        addr = nodenr_to_infiniband(config.nodes[x]) if config.server_infiniband else 'node{}'.format(config.nodes[x])
        for y in range(idr.num_procs_per_node()):
            ptl = port_to_leader + 2*y
            pte = port_to_elect + 2*y
            serverlist.append('server.{0}={1}:{2}:{3}'.format(srv_id, addr, ptl, pte))
            srv_id += 1

    ticktime         = 2000
    initlimit        = 10
    synclimit        = 5
    clientport       = 2181 + idr.identifier_local()

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
    config.datadir,
    clientport,
    '\n'.join(serverlist))

    with open(fs.join(loc.get_cfg_dir(), '{}.cfg'.format(config.gid)), 'w') as file:
        file.write(config_string)


# Starts Zookeeper, returns immediately after starting a thread containing our process
def boot(config):
    classpath = os.environ['CLASSPATH'] if 'CLASSPATH' in os.environ else ''
    prefix = ':'.join([
        loc.get_cfg_dir(),
        ':'.join([file for file in fs.ls(loc.get_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        ':'.join([file for file in fs.ls(loc.get_build_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        fs.join(loc.get_build_dir(), 'classes')])

    classpath = '{}:{}'.format(prefix, classpath)
    zoo_main = '-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.local.only=false org.apache.zookeeper.server.quorum.QuorumPeerMain'
    conf_location = fs.join(loc.get_cfg_dir(), str(config.gid)+'.cfg')

    command = 'java "-Dzookeeper.log.dir={}" "-Dzookeeper.root.logger={}" -cp "{}" {} "{}"'.format(config.log4j_loc, config.log4j_properties, classpath, zoo_main, conf_location)
    executor = Executor(command)
    executor.run(shell=True)

    fs.mkdir(config.datadir, exist_ok=True)
    with open(fs.join(config.datadir, 'myid'), 'w') as file: #Write myid file
        file.write(str(config.gid))
    return executor


# Stops Zookeeper instance
def stop(executor):
    return executor.stop()