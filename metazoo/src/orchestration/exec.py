import datetime
import time

from orchestration.orchestrator import instance as orch
from orchestration.registrar import instance as reg
import util.location as loc

# Hook to generate a timestamp for this experiment.
def timestamp_hook():
    # Obtain a timestamp for this experiment, and construct needed directories
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S')
    print('Timestamped experiment, designation {}'.format(timestamp))
    if fs.isdir(loc.get_metazoo_results_dir(), timestamp):
        if ui.ask_bool('Results already contain timestamp {}. Override (Y) or wait (n)?'):
            fs.rm(loc.get_metazoo_results_dir(), timestamp)
        else:
            while datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S') == timestamp:
                time.sleep(1)
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S')
            print('New timestamp assigned: {}'.format(timestamp))
    fs.mkdir(loc.get_metazoo_results_dir(), timestamp, str(x)) for x in range(repeats)
    reg['timestamp'] = timestamp

# Hook to clean the crawlspace directory, if it exists
# Should be performed in pre_experiment
def crawlspace_hook():
    fs.rm(loc.get_remote_crawlspace_dir(), ignore_errors=True)
    fs.mkdir(loc.get_remote_crawlspace_dir())

# Hook to load experiment and propagation commands
# Should be performed in pre_experiment
def load_experiment_hook():
    print('Loading experiment...', flush=True)
    experiment = exp.get_experiment()
    num_nodes_total = experiment.num_servers + experiment.num_clients

    aff_server = experiment.servers_core_affinity
    nodes_server = experiment.num_servers // aff_server
    reg['command_server'] = 'prun -np {} -{} python3 {} --exec_internal_server {}'.format(nodes_server, aff_server, fs.join(fs.abspath(), 'main.py'), '-d' if debug_mode else '')
    aff_client = experiment.clients_core_affinity
    nodes_client = experiment.num_clients // aff_client
    reg['command_client'] = 'prun -np {} -{} python3 {} --exec_internal_client {}'.format(nodes_client, aff_client, fs.join(fs.abspath(), 'main.py'), '-d' if debug_mode else '')
    reg['experiment'] = experiment


def pre_experiment_hook():
    reg['experiment'].pre_experiment()


def post_experiment_hook():
    reg['experiment'].post_experiment()
    reg['experiment'].clean()
