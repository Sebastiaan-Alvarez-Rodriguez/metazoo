# Code in this file is to boot, stop and maintain zookeeper servers
# A zookeeper server mainly needs a crawlspace, a config, a myid file, and a cleaner


import subprocess
import os

from remote.config import ServerConfig
import remote.util.identifier as idr
import remote.util.ip as ip
from util.executor import Executor
import util.fs as fs
import util.location as loc
from util.printer import *
import util.reader as rdr

# Populates uninitialized config members
def populate_config(config, debug_mode):
    config.datadir   = '{}/server{}/data'.format(loc.get_remote_crawlspace_dir(), config.gid)
    config.log4j_dir = loc.get_server_cfg_dir()
    config.log4j_properties = 'INFO, FILE'

# Generates a connectionlist, which client nodes read to decide which host to connect to 
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


'''
Checks if current server instance is the leader at invocation time.
Calls stat command through socket.

WARNING: A relatively large part of the time, 
the socket is not responding, or responds with empty string.
For that reason, we have retries. Still, better use _is_leader_logs().
This is what a response could look like:
    Zookeeper version: 3.3.0--1, built on 10/22/2020 15:44 GMT
    Clients:
     /127.0.0.1:38912[1](queued=0,recved=1,sent=0)
     /10.141.0.53:50820[1](queued=0,recved=1513242,sent=1862352)
    Latency min/avg/max: 0/0/222
    Received: 1513262
    Sent: 1862359
    Outstanding: 0
    Zxid: 0x1000b6d5a
    Mode: follower
    Node count: 6
'''
def _is_leader_socket(retries):
    outputs = []
    for x in range(retries):
        command = 'echo -e \'stat\' | nc localhost {}'.format(get_client_port())
        output = subprocess.check_output(command, shell=True).decode('utf-8')
        for line in output.split('\n'):
            if line.lstrip().startswith('Mode'):
                return line[6:].strip().lower() == 'leader'
        outputs.append(output)
    raise RuntimeError('Could not determine leader from outputs "{}"'.format(outputs))

'''
Detect whether we are a leader or not by reading the entire log.
This way is the only reliable way to tell whether this server is the leader.
This function is pretty slow. Still, it is better than the socket alternative.

NOTE: This only works on the server itself, because logs are local!
Lines giving an indication of being or not being leader could look like:
[SERVER] 2020-10-22 19:03:41,756 - INFO  [QuorumPeer:/0:0:0:0:0:0:0:0:2181:QuorumPeer@632] - FOLLOWING
[SERVER] 2020-10-22 18:59:58,859 - INFO  [QuorumPeer:/0:0:0:0:0:0:0:0:2181:QuorumPeer@644] - LEADING
'''
def _is_leader_logs(local_log):
    for line in rdr.reverse_readline(local_log):
        if line.endswith('FOLLOWING') or line.endswith('LEADING'):
            return line.endswith('LEADING')
    printw('Could not find out if server to kill is leader')
    return 'Unknown'

# Returns True if this node is the leader, False if it is a follower, "Unkown" if we cannot find out
def is_leader(local_log):
    return _is_leader_logs(local_log)

# Computes and returns client port
# Computed in such a way that multiple servers can share a host 
def get_client_port():
    return 2181 + (idr.num_procs_per_node()+1)*idr.identifier_local()

# Generates the Zookeeper config file for this server instance.
# Config is written to zookeeper-release-3.3.0/conf/<serverid>.cfg
def gen_zookeeper_config(config):
    ticktime         = 2000
    initlimit        = 10
    synclimit        = 5
    clientport       = get_client_port()

    config_string = '''
tickTime={}
initLimit={}
syncLimit={}
dataDir={}
clientPort={}
globalOutstandingLimit={}
{}'''.format(
    ticktime,
    initlimit,
    synclimit,
    config.datadir,
    clientport,
    250,
    '\n'.join(gen_serverlist(config)))

    with open(fs.join(loc.get_cfg_dir(), '{}.cfg'.format(config.gid)), 'w') as file:
        file.write(config_string)

# Writes the id of the server to the required 'myid' file in the crawlspace
# According to the documentation, this is how we assign ourselves a server id
def prepare_datadir(config):
    fs.mkdir(config.datadir, exist_ok=True)
    with open(fs.join(config.datadir, 'myid'), 'w') as file: #Write myid file
        file.write(str(config.gid))

# Boot zookeeper server, return executor to interact with the independent process
def boot(config, local_log):
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

    command = 'java "-Dzookeeper.log.dir={}" "-Dprops={}" "-Dfile={}" -cp "{}" {} "{}"'.format(
    config.log4j_dir,
    config.log4j_properties,
    local_log,
    classpath, 
    zoo_main, 
    conf_location)
    executor = Executor(command)
    executor.run(shell=True)

    return executor


# Clean old snapshots and logs from zookeeper while it is running 
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

# Stops server instance
def stop(executor):
    return executor.stop()