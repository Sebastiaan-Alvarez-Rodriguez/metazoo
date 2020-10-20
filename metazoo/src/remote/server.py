# Code in this file is executed on each server.
# The goal is to boot a zookeeper server, and make sure it knows of the other ones

import os

from remote.config import ServerConfig
import remote.identifier as idr
import remote.ip as ip
from util.executor import Executor
import util.fs as fs
import util.location as loc


# Populates uninitialized config members
def populate_config(config, debug_mode):
    config.datadir   = '{}/server{}/data'.format(loc.get_remote_crawlspace_dir(), config.gid)
    config.log4j_dir = loc.get_server_cfg_dir()
    config.log4j_properties = 'INFO, CONSOLE' if debug_mode else 'ERROR, CONSOLE'

def gen_connectionlist(config, experiment):
    # End goal:
    # <node101>:<clientport1>
    # <node101>:<clientport2>
    # <node102>:<clientport1>
    # <node102>:<clientport2>
    clientport = 2181
    serverlist = []
    for x in range(len(config.nodes) // idr.num_procs_per_node()):
        addr = ip.node_to_infiniband_ip(config.nodes[x]) if experiment.clients_use_infiniband else 'node{:03d}'.format(config.nodes[x]) 
        for y in range(idr.num_procs_per_node()):
            cport = clientport + (idr.num_procs_per_node()+1)*y
            serverlist.append('{}:{}'.format(addr, cport))
    return serverlist

# Generates a list of servers, which should be the same everywhere. Returns as list
def gen_serverlist(config):
    # End goal:
    # server.0=<ip1>:2182:2183 #share node1 cport=2181
    # server.1=<ip1>:2185:2186 #share node1 cport=2184
    # server.2=<ip2>:2182:2183 #share node2 cport=2181
    # server.3=<ip2>:2185:2186 #share node2 cport=2184
    # If we are server 1, then server.0 should have 'localhost' instead of <ip1>
    port_to_leader = 2182
    port_to_elect  = 2183

    serverlist = []
    srv_id = 0
    for x in range(len(config.nodes) // idr.num_procs_per_node()):
        addr = ip.node_to_infiniband_ip(config.nodes[x]) if config.server_infiniband else 'node{}'.format(config.nodes[x])
        for y in range(idr.num_procs_per_node()):
            ptl = port_to_leader + (idr.num_procs_per_node()+1)*y
            pte = port_to_elect + (idr.num_procs_per_node()+1)*y
            serverlist.append('server.{0}={1}:{2}:{3}'.format(srv_id, addr, ptl, pte))
            srv_id += 1
    return serverlist


# Generates the Zookeeper config file for this server instance.
# Config is written to zookeeper-release-3.3.0/conf/<serverid>.cfg
def gen_zookeeper_config(config):
    ticktime         = 2000
    initlimit        = 10
    synclimit        = 5
    clientport       = 2181 + (idr.num_procs_per_node()+1)*idr.identifier_local()

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
    '\n'.join(gen_serverlist(config)))

    with open(fs.join(loc.get_cfg_dir(), '{}.cfg'.format(config.gid)), 'w') as file:
        file.write(config_string)


def boot(config):
    classpath = os.environ['CLASSPATH'] if 'CLASSPATH' in os.environ else ''
    prefix = ':'.join([
        loc.get_cfg_dir(),
        config.log4j_dir,
        ':'.join([file for file in fs.ls(loc.get_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        ':'.join([file for file in fs.ls(loc.get_build_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        fs.join(loc.get_build_dir(), 'classes')])

    classpath = '{}:{}'.format(prefix, classpath)
    zoo_main = '-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.local.only=false org.apache.zookeeper.server.quorum.QuorumPeerMain'
    conf_location = fs.join(loc.get_cfg_dir(), str(config.gid)+'.cfg')

    fs.mkdir(config.datadir, exist_ok=True)
    with open(fs.join(config.datadir, 'myid'), 'w') as file: #Write myid file
        file.write(str(config.gid))

    command = 'java "-Dzookeeper.log.dir={}" "-Dprops={}" -cp "{}" {} "{}"'.format(
    config.log4j_dir,
    config.log4j_properties,
    classpath, 
    zoo_main, 
    conf_location)
    executor = Executor(command)
    executor.run(shell=True)

    return executor

def clean_data(config):
    classpath = os.environ['CLASSPATH'] if 'CLASSPATH' in os.environ else ''
    prefix = ':'.join([
        loc.get_cfg_dir(),
        config.log4j_dir,
        ':'.join([file for file in fs.ls(loc.get_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        ':'.join([file for file in fs.ls(loc.get_build_lib_dir(), only_files=True, full_paths=True) if file.endswith('.jar')]),
        fs.join(loc.get_build_dir(), 'classes')])

    classpath = '{}:{}'.format(prefix, classpath)
    zoo_main = '-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.local.only=false org.apache.zookeeper.server.PurgeTxnLog'

    command = 'java "-Dzookeeper.log.dir={}" "-Dprops={}" -cp "{}" {} "{}" "{}" "{}" > /dev/null 2>&1'.format(
        config.log4j_dir,
        config.log4j_properties,
        classpath, 
        zoo_main, 
        config.datadir,
        '-n',
        '4')
    os.system(command)
    # executor = Executor(command)
    # executor.run(shell=True)
    

# Stops Zookeeper instance
def stop(executor):
    return executor.stop()