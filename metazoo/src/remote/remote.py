import socket
import os

from dynamic.experiment import Experiment
from remote.config import Config, ServerConfig, ClientConfig
import remote.server as srv
import remote.client as cli
import util.fs as fs
import util.location as loc
import time

def get_remote():
    return 'dpsdas5LU'


# Assigns nodes in specific server and client lists in the config
def get_node_assignment(config, experiment):
    nodenumbers = [int(nodename[4:]) for nodename in os.environ['HOSTS'].split()]
    nodenumbers.sort()
    if not len(nodenumbers) == experiment.num_servers + experiment.num_clients:
        raise RuntimeError('Only {} nodes allocated for {} servers and {} clients'.format(len(nodenumbers), config.num_servers, config.num_clients))
    config.servers = nodenumbers[:experiment.num_servers] # The (alphabetically sorted) first X nodes will be the servers
    config.clients = nodenumbers[experiment.num_servers:] # The rest of the nodes will be the clients
 


# determine server id from the config
def get_server_id(config):
    try:
        return config.servers.index(int(socket.gethostname()[4:]))+1
    except ValueError as e:
        raise RuntimeError('Cannot fetch server id for this node, because this is a client')


# Constructs either a (server/client) config, populates it, and returns it
def construct_config(experiment):
    config = Config()
    get_node_assignment(config, experiment)
    if int(socket.gethostname()[4:]) in config.servers: # if hostname is in server list
        return ServerConfig(config, get_server_id(config)) # we have a server
    return ClientConfig(config) #otherwise, we have a client


def run():
    experiment = Experiment.load()
    config = construct_config(experiment)

    if isinstance(config, ServerConfig):
        if config.server_id == None:
            raise RuntimeError('Oh oh, should not happen')
        
        srv.populate_config(config)
        srv.gen_zookeeper_config(config)

        print('Server with id {} generated {}.cfg'.format(config.server_id, config.server_id), flush=True)
        executor = srv.boot(config)

        experiment.experiment_server(config.server_id)
        
        srv.stop(executor)
        #TODO: fix
        return True
        # return srv.run(config)
    else:
        time.sleep(4)
        cli.populate_config(config)
        executor = cli.boot(config)

        if config.host == None:
            raise RuntimeError('Oh oh , should not happen')

        experiment.experiment_client(config.host)
        cli.stop(executor)

        local_log = '.metazoo-log'
        if not fs.exists(loc.get_metazoo_log_dir()):
            fs.mkdir(loc.get_metazoo_log_dir())
            #TODO: client id?
        fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log + '0'))
        return True