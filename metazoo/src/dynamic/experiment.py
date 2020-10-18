import inspect

from dynamic.metazoo import MetaZoo
from experiments.interface import ExperimentInterface
import util.fs as fs
import util.importer as imp
import util.location as loc
import util.ui as ui

class Experiment(object):
    def __init__(self, location, modulename, clazz):
        self.location = location
        self.modulename = modulename
        self.instance = clazz()
        self._metazoo = MetaZoo()
        self._num_servers = None
        self._num_clients = None
        self._servers_use_infiniband = None
        self._clients_use_infiniband = None


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


    def clients_use_infiniband(self):
        if self._clients_use_infiniband == None:
            self._clients_use_infiniband = bool(self.instance.clients_use_infiniband())
        return self._clients_use_infiniband




    @property
    def metazoo(self):
        return self._metazoo

    

    def pre_experiment(self):
        val = self.instance.pre_experiment(self._metazoo)
        self.persist()
        return val


    def experiment_client(self, host):
        self._metazoo = MetaZoo.load() # Inside client node, must load persisted state
        self._metazoo.host = host
        return self.instance.experiment_client(self._metazoo)

    
    def experiment_server(self, server_id):
        self._metazoo = MetaZoo.load() # Inside server node, must load persisted state
        self._metazoo._id = server_id
        return self.instance.experiment_server(self._metazoo)


    def post_experiment(self):
        val = self.instance.post_experiment(self._metazoo)
        return val


    # Save all required information, so nodes can reconstruct our object
    def persist(self):
        self._metazoo.persist()
        with open(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), 'w') as file:
            file.write('{}|{}'.format(self.location, self.modulename))

    # Construct object from persisted information
    @staticmethod
    def load():
        with open(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'), 'r') as file:
            location, modulename = file.read().split('|')
            return get_experiment(location=location, modulename=modulename)

    # Cleans persisted information
    @staticmethod
    def clean():
        fs.rm(fs.join(loc.get_metazoo_experiment_dir(), '.elected.hidden'))


# Standalone function to get an experiment instance
def get_experiment(location=None, modulename=None):
    if location and modulename:
        for name, obj in inspect.getmembers(imp.import_full_path(location)):
            if name == modulename and inspect.isclass(obj) and issubclass(obj, ExperimentInterface):
                return Experiment(location, modulename, obj)
        raise RuntimeError('Could not fetch module "{}" in file {}'.format(modulename, location))

    candidates = []
    for item in fs.ls(loc.get_metazoo_experiment_dir(), full_paths=True, only_files=True):
        print('Processing item: '+item, flush=True)

        if  item.endswith(fs.join(fs.sep(), 'interface.py')) or not item.endswith('.py'):
            continue

        module = imp.import_full_path(item)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ExperimentInterface):
                candidates += ((item, name, obj),)

    for idx, x in enumerate(candidates):
        if x[2] == ExperimentInterface:
           del candidates[idx]

    if len(candidates) == 0:
        raise RuntimeError('Could not find a subclass of "ExperimentInterface" in directory {}. Make a ".py" file there, with a class extending "ExperimentInterface". See the example implementation for more details.'.format(loc.get_metazoo_experiment_dir()))
    elif len(candidates) == 1:
        return Experiment((candidates[0])[0], (candidates[0])[1], (candidates[0])[2])
    else:
        # TODO: If not pretty, can also get class name using obj.__name__
        idx = ui.ask_pick('Multiple suitable experiments found. Please pick an experiment:', [x[0] for x in candidates])
        return Experiment((candidates[idx])[0], (candidates[idx])[1], (candidates[idx])[2])