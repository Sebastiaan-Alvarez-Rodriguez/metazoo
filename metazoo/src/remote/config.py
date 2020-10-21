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
    def __init__(self, experiment, nodes):
        # List of server node numbers and client node numbers
        # (e.g. [114, 116,...],corresponding to 'node114' and 'node116' hosts)
        self._nodes = nodes

        self._server_infiniband = experiment.servers_use_infiniband
        self._client_infiniband = experiment.clients_use_infiniband

        self._gid = idr.identifier_global()
        self._lid = idr.identifier_local()

    @property
    def server_infiniband(self):
        return self._server_infiniband
    
    @property
    def client_infiniband(self):
        return self._client_infiniband

    @property
    def lid(self):
        return self._lid

    @property
    def gid(self):
        return self._gid

    @property
    def nodes(self):
        return self._nodes
    


class ServerConfig(Config):
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

    @property
    def datadir(self):
        return self._datadir
    
    @datadir.setter
    def datadir(self, value):
        self._datadir = value

    @property
    def log4j_dir(self):
        return self._log4j_dir
    
    @log4j_dir.setter
    def log4j_dir(self, value):
        self._log4j_dir = value

    @property
    def log4j_properties(self):
        return self._log4j_properties
    
    @log4j_properties.setter
    def log4j_properties(self, value):
        self._log4j_properties = value


class ClientConfig(Config):
    def __init__(self, experiment, nodes, hosts):
        super(ClientConfig, self).__init__(experiment, nodes)
        self._hosts = hosts
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

    @property
    def hosts(self):
        return self._hosts

    @property
    def log4j_dir(self):
        return self._log4j_dir

    @log4j_dir.setter
    def log4j_dir(self, value):
        self._log4j_dir = value
    
    @property
    def log4j_properties(self):
        return self._log4j_properties
    
    @log4j_properties.setter
    def log4j_properties(self, value):
        self._log4j_properties = value
