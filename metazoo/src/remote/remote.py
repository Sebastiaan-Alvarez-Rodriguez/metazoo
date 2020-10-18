from dynamic.experiment import Experiment
from remote.config import config_construct, ServerConfig, ClientConfig
import remote.server as srv
import remote.client as cli
import util.fs as fs
import util.location as loc
import time


def run():
    experiment = Experiment.load()
    config = config_construct(experiment)

    if isinstance(config, ServerConfig):
        srv.populate_config(config)
        srv.gen_zookeeper_config(config)

        executor = srv.boot(config)

        experiment.experiment_server(config.s_id)
        
        srv.stop(executor)
        #TODO: fix
        # local_log = '.metazoo-log'
        # if not fs.exists(loc.get_metazoo_log_dir()):
        #     fs.mkdir(loc.get_metazoo_log_dir())
        # fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_log_dir(), local_log + str(config.server_id)))
        return True
        # return srv.run(config)
    else:
        time.sleep(4)
        executor = cli.boot(config)
        experiment.experiment_client(config.host)
        cli.stop(executor)

        if config.host == None:
            raise RuntimeError('Oh oh , should not happen')
        return True