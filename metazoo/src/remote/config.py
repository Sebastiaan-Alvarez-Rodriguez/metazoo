import os
import socket

# Returns globally equivalent list of nodes with server and client designation
# The returned value is a tuple, with first a list of server nodes, and second a list of client nodes
def get_node_assignment(experiment):
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()
    if not len(nodenumbers) == experiment.num_servers + experiment.num_clients:
        raise RuntimeError('Only {} nodes allocated for {} servers and {} clients'.format(len(nodenumbers), config.num_servers, config.num_clients))
    return (nodenumbers[:experiment.num_servers], nodenumbers[experiment.num_servers:])


# Constructs either a (server/client) config, populates it, and returns it
def config_construct(experiment):
    config = Config(experiment)
    if int(socket.gethostname()[4:]) in config.servers: # if hostname is in server list
        return ServerConfig(config) # we have a server
    return ClientConfig(config) #otherwise, we have a client



class Config(object):
    def __init__(self, experiment):
        # List of server node numbers and client node numbers
        # (e.g. [114, 116,...],corresponding to 'node114' and 'node116' hosts)
        self.servers, self.clients = get_node_assignment(experiment)

        self.server_infiniband = experiment.servers_use_infiniband
        self.client_infiniband = experiment.clients_use_infiniband


class ServerConfig(object):
    def __init__(self, config):
        super(ServerConfig, self).__init__()
        self.cnf = config
        # Server id, used to globally identify this server. Must be equivalent everywhere
        try:
            self._s_id = config.servers.index(int(socket.gethostname()[4:]))+1
        except ValueError as e:
           raise RuntimeError('Cannot fetch server id for this node, because this is a client')


        # Directory containing data for this server
        self.datadir = None
        # Directory where log4j writes its logs, if we specify that log4j should write to file
        self.log4j_dir = None
        # Properties to hand to log4j
        self.log4j_properties = None

    @property
    def s_id(self):
        return self._s_id



class ClientConfig(object):
    def __init__(self, config):
        super(ClientConfig, self).__init__()
        self.cnf = config

        # Client id, used to globally identify this client. Must be equivalent everywhere
        try:
            self._c_id = len(config.servers)+config.clients.index(int(socket.gethostname()[4:]))+1
        except ValueError as e:
           raise RuntimeError('Cannot fetch server id for this node, because this is a client')

        self.host = 'node' + str(config.servers[0]) + ':2181'

    @property
    def c_id(self):
        return self._c_id