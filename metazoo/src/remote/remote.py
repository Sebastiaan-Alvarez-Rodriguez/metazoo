# Code in this file is the entrypoint for prun calls.
# run_server() and run_client() are called as soon as allocation is done.
# Goal of this file is to guide data processing on server and client nodes.


import time

from dynamic.experiment import Experiment
from remote.config import config_construct_server, config_construct_client, ServerConfig, ClientConfig
import remote.client as cli
import remote.server as srv
import remote.util.identifier as idr
from remote.util.syncer import Syncer
import util.fs as fs
import util.location as loc
from util.repeater import Repeater

# Controls server nodes. Executed by all servers.
def run_server(debug_mode):
    experiment = Experiment.load()
    timestamp = experiment.timestamp
    repeats = experiment.metazoo.repeats

    config = config_construct_server(experiment)
    srv.populate_config(config, debug_mode)
    if config.gid == 0:
        print('Network booted. Orchestrator ready!', flush=True)
        with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'w') as file:
            file.write('\n'.join(srv.gen_connectionlist(config, experiment)))

    syncer = Syncer(config, experiment, 'server', debug_mode)

    # All servers must generate a config
    srv.gen_zookeeper_config(config)
    # All servers must write their myid file
    srv.prepare_datadir(config)

    global_status = True
    for repeat in range(repeats):

        # Make/clean a directory on a local node disk to log quickly.
        # Only one process on a node has to do this
        if config.lid == 0:
            fs.rm(loc.get_node_log_dir(), ignore_errors=True)
            fs.mkdir(loc.get_node_log_dir(), exist_ok=True)

        # Must wait and synchronise with all servers and clients
        syncer.sync()
        

        local_log = fs.join(loc.get_node_log_dir(), 'server{}.log'.format(config.gid))
        executor = srv.boot(config, local_log)
        
        # If cleaning is requested, boot cleaner service
        if experiment.server_periodic_clean > 0:
            clean_repeater = Repeater(lambda: srv.clean_data(config), experiment.server_periodic_clean)
            clean_repeater.start()


        experiment.experiment_server(config, executor, repeat, lambda: srv.is_leader(local_log))
        status = srv.stop(executor)
        
        # If cleaning is requested, stop cleaner service
        if experiment.server_periodic_clean > 0:
            clean_repeater.stop()

        global_status &= status

        # Write server log to zookeeper/metazoo/results/<repeat>/
        if fs.isfile(local_log):
            fs.mv(local_log, fs.join(loc.get_metazoo_results_dir(), timestamp, repeat, fs.basename(local_log)))
        
        if config.gid == 0:
            print('Server iteration {}/{} complete'.format(repeat+1, repeats), flush=True)
        
        # We log failed executions in a results/<timestamp>/failures.metalog
        if not status:
            print('[WARNING] Server {} status in iteration {}/{} not good'.format(config.gid, repeat, repeats-1), flush=True)
            with open(fs.join(loc.get_metazoo_results_dir(), timestamp, 'failures.metalog'), 'a') as file:
                file.write('server:{}:{}\n'.format(config.gid, repeat))

    syncer.close()

    # Delete sync dir and communication file
    if config.gid == 0:
        fs.rm(loc.get_cfg_dir(), '.metazoo.cfg')

    return global_status


# Controls client nodes. Executed by all clients.
def run_client(debug_mode):
    experiment = Experiment.load()
    timestamp = experiment.timestamp
    repeats = experiment.metazoo.repeats

    myid = idr.identifier_global()
    #  We must wait until the servers make themselves known
    while not fs.isfile(loc.get_cfg_dir(), '.metazoo.cfg'):
        time.sleep(1)

    with open(fs.join(loc.get_cfg_dir(), '.metazoo.cfg'), 'r') as file:
        # <node101>:<clientport1>
        hosts = [line.strip() for line in file.readlines()]
    
    config = config_construct_client(experiment, hosts)
    cli.populate_config(config, debug_mode)
    
    syncer = Syncer(config, experiment, 'client', debug_mode)

    global_status = True
    for repeat in range(repeats):
        # We make a directory on a local node disk to log quickly.
        # Only one process on a node has to do this
        if config.lid == 0:
            fs.mkdir(loc.get_node_log_dir(), exist_ok=True)

        # Must wait and synchronise with all servers and clients
        
        if debug_mode: print('Client {} stage PRE_SYNC'.format(myid), flush=True)
        syncer.sync()
        if debug_mode: print('Client {} stage POST_SYNC'.format(myid), flush=True)
        
        executor = cli.boot(config)
        experiment.experiment_client(config, executor, repeat)
        status = cli.stop(executor)
        global_status &= status

        local_log = fs.join(loc.get_node_log_dir(), '{}.log'.format(config.gid))
        # Move the client log file (if it exists) from local disk to shared storage
        if fs.isfile(local_log):
            fs.mv(fs.join(loc.get_node_log_dir(), local_log), fs.join(loc.get_metazoo_results_dir(), timestamp, repeat, fs.basename(local_log)))

        # We log failed executions in a results/<timestamp>/failures.metalog
        if not status:
            print('[WARNING] Client {} status in iteration {}/{} not good'.format(config.gid, repeat, repeats-1), flush=True)
            with open(fs.join(loc.get_metazoo_results_dir(), timestamp, 'failures.metalog'), 'a') as file:
                file.write('server:{}:{}\n'.format(config.gid, repeat))
    syncer.close()
    return global_status