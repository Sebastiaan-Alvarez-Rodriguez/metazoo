import inspect
import sys

from dynamic.metazoo import MetaZoo
from experiments.interface import ExperimentInterface
import util.fs as fs
import util.importer as imp
import util.location as loc
import util.ui as ui


class Experiment(object):
    '''
    Object to handle communication with user-defined experiment interface
    Almost all attributes are lazy, so the dynamic code is used minimally.
    '''
    def __init__(self, timestamp, location, clazz):
        self.timestamp = timestamp
        self.location = location
        self.instance = clazz()
        self._metazoo = MetaZoo()
        self._num_servers = None
        self._num_clients = None
        self._servers_use_infiniband = None
        self._clients_use_infiniband = None
        self._servers_core_affinity = None
        self._clients_core_affinity = None

        self._server_periodic_clean = None

    @property
    def num_servers(self):
        if self._num_servers == None:
            self._num_servers = int(self.instance.num_servers())
            if self._num_servers < 2:
                raise RuntimeError('Experiment must specify num_servers >=2 (currently got {})'.format(self._num_servers))
        return self._num_servers

    @property
    def num_clients(self):
        if self._num_clients == None:
            self._num_clients = int(self.instance.num_clients())
            if self._num_clients < 1:
                raise RuntimeError('Experiment must specify num_clients >=1 (currently got {})'.format(self._num_clients))
        return self._num_clients
    
    @property
    def servers_use_infiniband(self):
        if self._servers_use_infiniband == None:
            self._servers_use_infiniband = bool(self.instance.servers_use_infiniband())
        return self._servers_use_infiniband

    @property
    def clients_use_infiniband(self):
        if self._clients_use_infiniband == None:
            self._clients_use_infiniband = bool(self.instance.clients_use_infiniband())
        return self._clients_use_infiniband

    @property
    def servers_core_affinity(self):
        if self._servers_core_affinity == None:
            self._servers_core_affinity = int(self.instance.servers_core_affinity())
            if self._servers_core_affinity < 1:
                raise RuntimeError('Experiment must specify servers_core_affinity >= 1 (currently got {})'.format(self._servers_core_affinity))
            if self.num_servers % self._servers_core_affinity != 0:
                raise RuntimeError('Number of servers must be divisible by server core affinity. {} % {} = {} != 0'.format(self.num_servers, sef._servers_core_affinity, (self.num_servers % self._servers_core_affinity)))
        return self._servers_core_affinity

    @property
    def clients_core_affinity(self):
        if self._clients_core_affinity == None:
            self._clients_core_affinity = int(self.instance.clients_core_affinity())
            if self._clients_core_affinity < 1:
                raise RuntimeError('Experiment must specify clients_core_affinity >= 1 (currently got {})'.format(self._clients_core_affinity))
            if self.num_clients % self._clients_core_affinity != 0:
                raise RuntimeError('Number of clients must be divisible by client core affinity. {} % {} = {} != 0'.format(self.num_clients, sef._clients_core_affinity, (self.num_clients % self._clients_core_affinity)))
        return self._clients_core_affinity

    @property
    def server_periodic_clean(self):
        if self._server_periodic_clean == None:
            self._server_periodic_clean = int(self.instance.server_periodic_clean())
            if self._server_periodic_clean < 0:
                raise RuntimeError('Server periodic clean designation must be either 0 (never clean) or an integer representing time (s)')
        return self._server_periodic_clean

    @property
    def metazoo(self):
        return self._metazoo


    def pre_experiment(self, repeats):
        self._metazoo._repeats = repeats
        val = self.instance.pre_experiment(self._metazoo)
        self.persist()
        return val


    def get_client_run_command(self, config, repeat):
        self._metazoo._gid = config.gid
        self._metazoo._lid = config.lid
        self._metazoo._hosts = tuple(config.hosts)
        self._metazoo._repeat = repeat
        self._metazoo._log_location = fs.join(loc.get_metazoo_results_dir(), self.timestamp, repeat, 'experiment_logs')
        return self.instance.get_client_run_command(self._metazoo)


    def experiment_client(self, config, executor, repeat):
        self._metazoo._gid = config.gid
        self._metazoo._lid = config.lid
        self._metazoo._hosts = tuple(config.hosts)
        self._metazoo._executor = executor
        self._metazoo._repeat = repeat
        self._metazoo._log_location = fs.join(loc.get_metazoo_results_dir(), self.timestamp, repeat, 'experiment_logs')

        return self.instance.experiment_client(self._metazoo)


    def experiment_server(self, config, executor, repeat, is_leader_func):
        self._metazoo._gid = config.gid
        self._metazoo._lid = config.lid
        self._metazoo._executor = executor
        self._metazoo._repeat = repeat
        self._metazoo._log_location = fs.join(loc.get_metazoo_results_dir(), self.timestamp, repeat, 'experiment_logs')
        self._metazoo._is_leader_func = is_leader_func
        return self.instance.experiment_server(self._metazoo)


    def post_experiment(self):
        val = self.instance.post_experiment(self._metazoo)
        return val


    # Save all required information, so nodes can reconstruct our object
    def persist(self):
        self._metazoo.persist()
        fs.rm(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), ignore_errors=True)
        with open(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), 'w') as file:
            file.write('{}|{}'.format(self.timestamp, self.location))

    # Construct object from persisted information
    @staticmethod
    def load():
        with open(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), 'r') as file:
            timestamp, location = file.read().split('|')
            exp = load_experiment(timestamp, location)
            exp._metazoo = MetaZoo.load()
            return exp

    # Cleans persisted information
    def clean(self):
        fs.rm(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), ignore_errors=True)
        self._metazoo.clean()


# Loads an experiment in the node stage and returns it
def load_experiment(timestamp, location):
    module = imp.import_full_path(location)
    try:
        return Experiment(timestamp, location, module.get_experiment())
    except AttributeError as e:
        raise RuntimeError('Could not fetch Experiment module in file {}. Did you define get_experiment() there?'.format(location))


# Standalone function to get an experiment instance
def get_experiments(timestamp):
  
    candidates = []
    for item in fs.ls(loc.get_metazoo_experiment_dir(), full_paths=True, only_files=True):
        if item.endswith(fs.join(fs.sep(), 'interface.py')) or not item.endswith('.py'):
            continue
        try:
            module = imp.import_full_path(item)
            candidates.append((item, module.get_experiment(),))
        except AttributeError:
            print('Item had no get_experiment(): {}'.format(item))

    if len(candidates) == 0:
        raise RuntimeError('Could not find a subclass of "ExperimentInterface" in directory {}. Make a ".py" file there, with a class extending "ExperimentInterface". See the example implementation for more details.'.format(loc.get_metazoo_experiment_dir()))
    elif len(candidates) == 1:
        return [Experiment(timestamp, candidates[0][0], candidates[0][1])]
    else:
        idcs = ui.ask_pick_multiple('Multiple suitable experiments found. Please pick experiments:', [x[0] for x in candidates])
        return [Experiment(timestamp+'_'+str(idx), (candidates[x])[0], (candidates[x])[1]) for idx, x in enumerate(idcs)]