from experiments.interface import ExperimentInterface
import remote.server as srv
import util.fs as fs
import util.location as loc
import os
import time

class ExampleExperiment(ExperimentInterface):
    '''
    A most useful experiment.
    Check <root dir>/metazoo/experiments/example_simple/example.py 
    for an example implementation.
    Also, check <root dir>/metazoo/dynamic/metazoo.py
    to find out how metazoo variables work.
    '''
    def num_servers(self):
        '''Get amount of server nodes to allocate'''
        return 2

    def num_clients(self):
        '''get amount of client nodes to allocate'''
        return 1


    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        print('Hi there! I am executed before the experiment starts!')

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        print('Hello from client, I will connect to:{}.'.format(metazoo.host))
        time.sleep(8) #Client remains active for a while
        

    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        print('I am server {}, and I am running ZooKeeper now...'.format(metazoo.id))
        time.sleep(8) #Server remains active for a while


    def post_experiment(self, metazoo):
        print('Experiments are done')