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

    # Write communication file for clients to read
    if config.gid == 0:
        with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'w') as file:
            file.write('\n'.join(srv.gen_connectionlist(config)))

    srv.populate_config(config)
    srv.gen_zookeeper_config(config)

    executor = srv.boot(config)

    experiment.experiment_server(config)
    
    srv.stop(executor)

    # Delete communication file
    if config.gid == 0:
        fs.rm(loc.get_cfg_dir(), '.metazoo.cfg')
    #TODO: fix
    # local_log = '.metazoo-log'
    # if not fs.exists(loc.get_metazoo_log_dir()):
    #     fs.mkdir(loc.get_metazoo_log_dir())
    # fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log + str(config.server_id)))
    return True
    # return srv.run(config)

def run_client():
    experiment = Experiment.load()

    while not fs.isfile(loc.get_cfg_dir(), '.metazoo.cfg'):
        time.sleep(1) # We must wait until the servers make themselves known

    with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'r') as file:
        # server.0=<ip1>:<clientport> --> <ip1>:<clientport>
        hosts = [line.split('=')[1] for line in file.readlines()]

    config = config_construct_client(experiment, hosts)
    time.sleep(4)

    executor = cli.boot(config)
    experiment.experiment_client(config)
    cli.stop(executor)

    if config.host == None:
        raise RuntimeError('Oh oh , should not happen')
    return True