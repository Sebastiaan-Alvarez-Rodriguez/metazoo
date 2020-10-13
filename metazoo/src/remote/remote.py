import socket
import os

from dynamic.experiment import Experiment
from remote.config import Config, ServerConfig
import remote.server as srv
import util.fs as fs

def get_remote():
    return 'dpsdas5LU'


# Assigns nodes in specific server and client lists in the config
def get_node_assignment(config):
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()
    if not len(nodenumbers) == config.num_servers + config.num_clients:
        raise RuntimeError('Only {} nodes allocated for {} servers and {} clients'.format(len(nodenumbers), config.num_servers, config.num_clients))
    config.servers = nodenumbers[:config.num_servers]
    config.clients = nodenumbers[config.num_servers:]


# Returns True if the calling instance has server designation, False otherwise
def is_server(config):
    return int(socket.gethostname()[4:]) in config.servers 


# determine server id from the config
def get_server_id(config):
    try:
        return config.servers.index(int(socket.gethostname()[4:]))+1
    except ValueError as e:
        raise RuntimeError('Cannot fetch server id for this node, because this is a client')


# Constructs either a (server/client) config, populates it, and returns it
def construct_config():
    config = Config()
    get_node_assignment(config)
    if is_server(config):
        return ServerConfig(config, get_server_id(config))
    else:
        pass #TODO: Does a client need configuration?
    return config


def run():
    config = construct_config()
    if isinstance(config, ServerConfig):
        experiment = Experiment.load()
        if config.server_id == None:
            raise RuntimeError('Oh oh , should not happen')
        experiment.experiment_server(config.server_id)
        local_log = '.metazoo-log'
        fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log + str(config.server_id)))
        return True
        # return srv.run(config)
    else:
        pass #TODO: Construct client to run
        return True