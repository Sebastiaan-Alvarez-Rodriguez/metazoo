from dynamic.experiment import Experiment
from remote.config import config_construct_server, config_construct_client, ServerConfig, ClientConfig
import remote.server as srv
import remote.client as cli
import util.fs as fs
import util.location as loc
import time

def run_server():
    experiment = Experiment.load()
    config = config_construct_server(experiment)
    srv.populate_config(config)
    srv.gen_zookeeper_config(config)

    executor = srv.boot(config)

    experiment.experiment_server(config)
    
    srv.stop(executor)
    #TODO: fix
    # local_log = '.metazoo-log'
    # if not fs.exists(loc.get_metazoo_log_dir()):
    #     fs.mkdir(loc.get_metazoo_log_dir())
    # fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log + str(config.server_id)))
    return True
    # return srv.run(config)

def run_client():
    experiment = Experiment.load()
    config = config_construct_client(experiment)
    time.sleep(4)
    executor = cli.boot(config)
    experiment.experiment_client(config)
    cli.stop(executor)

    if config.host == None:
        raise RuntimeError('Oh oh , should not happen')
    return True