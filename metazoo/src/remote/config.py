from parse.parser import Parser

class Config(object):
    def __init__(self):
        parser = Parser() 
        # List of server node numbers
        # (e.g. [114, 116,...],corresponding to 'node114' and 'node116' hosts)
        self.servers = None
        # List of client node numbers
        self.clients = None

        self.server_infiniband = parser.servers_use_infiniband
        self.client_infiniband = parser.clients_use_infiniband


class ServerConfig(object):
    def __init__(self, config, server_id):
        super(ServerConfig, self).__init__()
        self.cnf = config
        # Server id, used to globally identify this server. Must be equivalent everywhere
        self.server_id = server_id
        # Directory containing data for this server
        self.datadir = None
        # Directory where log4j writes its logs, if we specify that log4j should write to file
        self.log4j_dir = None
        # Properties to hand to log4j
        self.log4j_properties = None


class ClientConfig(object):
    def __init__(self, config):
        super(ClientConfig, self).__init__()
        self.cnf = config
        self.host = 'node' + str(config.servers[0]) + ':2181'
        self.log4j_dir = None