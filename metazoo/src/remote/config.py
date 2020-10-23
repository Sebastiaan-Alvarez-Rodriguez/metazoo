import abc
import os
import socket

import remote.util.identifier as idr


# Constructs a client config, populates it, and returns it
def config_construct_client(experiment, hosts):
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()
    if not len(nodenumbers) == experiment.num_clients:
        raise RuntimeError('Allocated incorrect number of nodes ({}) for {} clients'.format(len(nodenumbers), experiment.num_clients))
    return ClientConfig(experiment, nodenumbers, hosts)

# Constructs a server config, populates it, and returns it
def config_construct_server(experiment):
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()
    if not len(nodenumbers) == experiment.num_servers:
        raise RuntimeError('Allocated incorrect number of nodes ({}) for {} servers'.format(len(nodenumbers), experiment.num_servers))
    return ServerConfig(experiment, nodenumbers)


class Config(metaclass=abc.ABCMeta):
    '''
    Base config class. Config implementations should extend this class,
    since it provides storage for and access to
    essential variables vor servers and clients.
    '''
    def __init__(self, experiment, nodes):
        self._nodes = nodes

        self._server_infiniband = experiment.servers_use_infiniband
        self._client_infiniband = experiment.clients_use_infiniband

        self._gid = idr.identifier_global()
        self._lid = idr.identifier_local()

    # True if servers should communicate using infiniband, False otherwise
    @property
    def server_infiniband(self):
        return self._server_infiniband
    
    # True if clients should communicate with servers using infiniband, False otherwise
    @property
    def client_infiniband(self):
        return self._client_infiniband

    # Local id, different for each allocated process on the same node
    @property
    def lid(self):
        return self._lid

    # Global id, different for each grouped allocated process
    @property
    def gid(self):
        return self._gid

    # Sorted list of server node numbers and client node numbers
    # (e.g. [114, 116,...],corresponding to 'node114' and 'node116' hosts)
    @property
    def nodes(self):
        return self._nodes



class ServerConfig(Config):
    '''Config implementation for servers'''

    def __init__(self, experiment, nodes):
        super(ServerConfig, self).__init__(experiment, nodes)
        # Directory containing data for this server
        self._datadir = None
        # Directory where log4j writes its logs, if we specify that log4j should write to file
        self._log4j_dir = None
        self._log4j_properties = None

    @property
    def server_infiniband(self):
        return super().server_infiniband
    
    @property
    def client_infiniband(self):
        return super().client_infiniband

    @property
    def lid(self):
        return super().lid

    @property
    def gid(self):
        return super().gid

    @property
    def nodes(self):
        return super().nodes

    # datadir value of this server's config. Essentially the crawlspace pointer
    @property
    def datadir(self):
        return self._datadir
    
    @datadir.setter
    def datadir(self, value):
        self._datadir = value

    # Path to directory containing log4j path
    @property
    def log4j_dir(self):
        return self._log4j_dir
    
    @log4j_dir.setter
    def log4j_dir(self, value):
        self._log4j_dir = value

    # Rootlogger properties, e.g. 'INFO, FILE' or 'ERROR, CONSOLE'
    @property
    def log4j_properties(self):
        return self._log4j_properties
    
    @log4j_properties.setter
    def log4j_properties(self, value):
        self._log4j_properties = value


class ClientConfig(Config):
    '''Config implementation for clients'''

    def __init__(self, experiment, nodes, hosts):
        super(ClientConfig, self).__init__(experiment, nodes)
        self._hosts = hosts

    @property
    def server_infiniband(self):
        return super().server_infiniband
    
    @property
    def client_infiniband(self):
        return super().client_infiniband

    @property
    def lid(self):
        return super().lid

    @property
    def gid(self):
        return super().gid

    @property
    def nodes(self):
        return super().nodes

    # List of servers running. Each server is listed as '<ip>:<port>'
    @property
    def hosts(self):
        return self._hosts