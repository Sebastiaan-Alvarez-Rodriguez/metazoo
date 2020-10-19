from experiments.interface import ExperimentInterface
import remote.server as srv
import util.fs as fs
import util.location as loc
import os
import time
import random

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

    def servers_use_infiniband(self):
        '''True if servers must communicate with eachother over infiniband, False otherwise'''
        return False

    def clients_use_infiniband(self):
        '''True if clients must communicate with servers over infinband, False otherwise'''
        return False

    def servers_core_affinity(self):
        '''Amount of server processes which may be mapped on the same physical node'''
        return 2

    def clients_core_affinity(self):
        '''Amount of client processes which may be mapped on the same physical node'''
        return 1


    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        print('Hi there! I am executed before the experiment starts!')
        metazoo.register['time'] = 30
        nr_kills = 7
        metazoo.register['nr_kills'] = nr_kills
        metazoo.register['kills'] = [random.randint(0, self.num_servers()-1) for x in range(nr_kills)]
        print('Running for {}s, killing: {}'.format(metazoo.register['time'], metazoo.register['kills']), flush=True)

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        print('Hello from client, I will connect to:{}.'.format(metazoo.host), flush=True)
        sleep_time = metazoo.register['time']
        time.sleep(sleep_time) #Client remains active for a while
        print('Shutting down client', flush=True)
        metazoo.executor.stop()
        

    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        print('I am server {}, and I am running ZooKeeper now...'.format(metazoo.gid), flush=True) 
        nap_time = metazoo.register['time'] / (metazoo.register['nr_kills']+1)
        kills = metazoo.register['kills']
        time.sleep(nap_time)
        for kill in kills:
            if kill == metazoo.gid:
                metazoo.executor.reboot()
            time.sleep(nap_time)


    def post_experiment(self, metazoo):
        print('Experiments are done')