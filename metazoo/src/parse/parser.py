import configparser

import util.location as loc
import util.fs as fs
import util.ui as ui


class Parser(object):
    '''Simple object to provide access to persisting variables'''

    def __init__(self):
        config_loc = fs.join(loc.get_metazoo_config_dir(), 'metazoo.cfg')
        if not fs.isfile(config_loc):
            write_config(config_loc)

        self.parser = configparser.ConfigParser()
        self.parser.read(config_loc)

    @property
    def num_servers(self):
        return int(self.parser['Orchestration']['num_servers'])

    @property
    def num_clients(self):
        return int(self.parser['Orchestration']['num_clients'])

    @property
    def servers_use_infiniband(self):
        return self.parser['Communication']['servers_use_infiniband']

    @property
    def clients_use_infiniband(self):
        return self.parser['Communication']['clients_use_infiniband']


# Ask user questions to generate a config
def gen_config():
    num_clients = ui.ask_int('How many Zookeeper Client nodes do you want to allocate?', minval=1)
    num_servers = ui.ask_int('How many Zookeeper Server nodes do you want to allocate?', minval=1)
    servers_use_infiniband = ui.ask_bool('Do you want servers to communicate using infiniband?')
    clients_use_infiniband = ui.ask_bool('Do you want clients to communicate with servers using infiniband?')
    write_config(config_loc, num_servers, num_clients, servers_use_infiniband, clients_use_infiniband)


# Persist a configuration file
def write_config(config_loc, num_servers=2, num_clients=2, servers_use_infiniband=True, clients_use_infiniband=False):
    parser = configparser.ConfigParser()
    parser['Orchestration'] = {
        'num_servers': num_servers,
        'num_clients': num_clients
    }
    parser['Communication'] = {
        'servers_use_infiniband': servers_use_infiniband,
        'clients_use_infiniband': clients_use_infiniband
    }
    with open(config_loc, 'w') as file:
        parser.write(file)


# Check if a config exists
def check_config():
    return fs.isfile(fs.join(loc.get_metazoo_config_dir(), 'metazoo.cfg'))


# Return number of nodes stored by configuration
def get_num_nodes():
    parser = Parser()
    return parser.num_clients+parser.num_servers