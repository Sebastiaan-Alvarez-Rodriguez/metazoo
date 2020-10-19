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
        return 5

    def num_clients(self):
        '''get amount of client nodes to allocate'''
        return 256

    def servers_use_infiniband(self):
        '''True if servers must communicate with eachother over infiniband, False otherwise'''
        return True

    def clients_use_infiniband(self):
        '''True if clients must communicate with servers over infinband, False otherwise'''
        return False

    def servers_core_affinity(self):
        '''Amount of server processes which may be mapped on the same physical node'''
        return 1

    def clients_core_affinity(self):
        '''Amount of client processes which may be mapped on the same physical node'''
        return 16
# prc / prcs per core = allocation
# 256 /            16 = 16
# 250 /            10 = 25 -> too much
# 250 /            25 = 10 -> too little
# 252 /             X = 18 -> 18X = 252 -> X = 252/18 -> X = 14 -> too much
# 260 /             X = 20 -> 20X = 260 -> X = 260/20 -> X = 13 -> too much

    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        metazoo.register['time'] = 50
        nr_kills = 3
        metazoo.register['nr_kills'] = nr_kills
        metazoo.register['kills'] = [random.randint(0, self.num_servers()-1) for x in range(nr_kills)]
        print('Running for {}s, killing: {}'.format(metazoo.register['time'], metazoo.register['kills']), flush=True)

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        sleep_time = metazoo.register['time']
        time.sleep(sleep_time) #Client remains active for a while
        metazoo.executor.stop()
        

    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        nap_time = metazoo.register['time'] / (metazoo.register['nr_kills']+1)
        kills = metazoo.register['kills']
        time.sleep(2*nap_time)
        for kill in kills:
            if kill == metazoo.gid:
               metazoo.executor.reboot()
            time.sleep(nap_time)
        time.sleep(nap_time)


    def post_experiment(self, metazoo):
        print('Experiments are done')