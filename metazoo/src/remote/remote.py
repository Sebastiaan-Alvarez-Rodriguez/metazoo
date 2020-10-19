from dynamic.experiment import Experiment
from remote.config import config_construct_server, config_construct_client, ServerConfig, ClientConfig
import remote.server as srv
import remote.client as cli
import util.fs as fs
import util.location as loc
import time


def run_server(debug_mode):
    experiment = Experiment.load()
    config = config_construct_server(experiment)

    # Write communication file for clients to read
    if config.gid == 0:
        with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'w') as file:
            file.write('\n'.join(srv.gen_connectionlist(config, experiment)))

    srv.populate_config(config, debug_mode)
    srv.gen_zookeeper_config(config)

    executor = srv.boot(config)

    experiment.experiment_server(config, executor, lambda: srv.clean_data(config))
    
    status = srv.stop(executor)

    # Delete communication file
    if config.gid == 0:
        fs.rm(loc.get_cfg_dir(), '.metazoo.cfg')
    return status
    
def run_client(debug_mode):
    experiment = Experiment.load()

    while not fs.isfile(loc.get_cfg_dir(), '.metazoo.cfg'):
        time.sleep(1) # We must wait until the servers make themselves known

    with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'r') as file:
        # <node101>:<clientport1>
        hosts = [line.split('|')[experiment.clients_use_infiniband].strip() for line in file.readlines()]

    config = config_construct_client(experiment, hosts)
    cli.populate_config(config, debug_mode)
    time.sleep(4) # We seriously need to wait for servers to boot up, give them a few seconds

    executor = cli.boot(config)
    experiment.experiment_client(config, executor)
    status = cli.stop(executor)

    local_log = '{}.log'.format(config.gid)
    if fs.isfile(loc.get_node_log_dir(), local_log):
        fs.mkdir(loc.get_metazoo_log_dir(), exist_ok=True)
        fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log))
    return status