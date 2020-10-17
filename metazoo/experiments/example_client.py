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
    def get_client_loc(self):
        return fs.join(fs.abspath(), 'src', 'client', 'out', 'artifacts', 'client_jar', 'client.jar')

    def num_servers(self):
        '''Get amount of server nodes to allocate'''
        return 3

    def num_clients(self):
        '''get amount of client nodes to allocate'''
        return 1


    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        print('Hi there! I am executed before the experiment starts!')

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        print('Hello from client, I will connect to:{}.'.format(metazoo.host))
        classpath = fs.join(loc.get_build_dir(), 'zookeeper-3.3.0.jar')
        os.system('java -cp "{}" -jar {} {}'.format(classpath, self.get_client_loc(), metazoo.host))
        
    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        print('I am server {}, and I am running ZooKeeper now...'.format(metazoo.id))
        time.sleep(5)


    def post_experiment(self, metazoo):
        print('Experiments are done')