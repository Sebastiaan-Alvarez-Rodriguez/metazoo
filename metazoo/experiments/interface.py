import abc


class ExperimentInterface(metaclass=abc.ABCMeta):
    '''
    This interface provides hooks, which get triggered on specific moments in execution.
    Experiments must be defined inside this interface.
    MetaZoo dynamically imports and executes it.

    Check <root dir>/metazoo/experiments/example_simple/example.py 
    for an example implementation.
    Also, check <root dir>/metazoo/dynamic/metazoo.py
    to find out how metazoo variables work.
    '''
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'num_servers') and callable(subclass.num_servers) and 
                hasattr(subclass, 'num_clients') and callable(subclass.num_clients) and 
                hasattr(subclass, 'pre_experiment') and callable(subclass.pre_experiment) and 
                hasattr(subclass, 'experiment_client') and callable(subclass.experiment_client) and 
                hasattr(subclass, 'experiment_server') and callable(subclass.experiment_server) and 
                hasattr(subclass, 'post_experiment') and callable(subclass.post_experiment) or NotImplemented)

    @abc.abstractmethod
    def num_servers(self):
        '''Get amount of server nodes to allocate'''
        raise NotImplementedError

    @abc.abstractmethod
    def num_clients(self):
        '''get amount of client nodes to allocate'''
        raise NotImplementedError

    @abc.abstractmethod
    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        raise NotImplementedError

    @abc.abstractmethod
    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        raise NotImplementedError

    @abc.abstractmethod
    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        raise NotImplementedError


    @abc.abstractmethod
    def post_experiment(self, metazoo):
        '''Execution after experiment finishes. Executed no the remote once.'''
        raise NotImplementedError