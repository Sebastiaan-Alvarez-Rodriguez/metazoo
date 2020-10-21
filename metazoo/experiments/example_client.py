import os
import random
import threading
import time

from experiments.interface import ExperimentInterface
import remote.client as cli
import util.fs as fs
import util.location as loc

class ExampleExperiment(ExperimentInterface):
    '''
    A most useful experiment.
    Check <root dir>/metazoo/experiments/examples/example_simple.py 
    for an example implementation.
    Also, check <root dir>/metazoo/dynamic/metazoo.py
    to find out how metazoo variables work.
    '''
    def num_servers(self):
        '''Get amount of server nodes to allocate'''
        return 3

    def num_clients(self):
        '''get amount of client nodes to allocate'''
        return 4

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
        return 2
# prc / prcs per core = allocation
# 256 /             8 = 32
# 250 /            10 = 25
# 260 /            13 = 20 
# 252 /            14 = 18
# 256 /            16 = 16
# 250 /            25 = 10

    def server_periodic_clean(self):
        '''Period in seconds for servers to clean their crawlspaces. 0 means no cleaning'''
        return 10


    def pre_experiment(self, metazoo):
        cli.prepare_classpath_symlinks()
        '''Execution before experiment starts. Executed on the remote once.'''
        metazoo.register['time'] = 30
        nr_kills = 2
        metazoo.register['nr_kills'] = nr_kills
        metazoo.register['kills'] = [random.randint(0, self.num_servers()-1) for x in range(nr_kills)]
        print('Running for {}s, killing: {}'.format(metazoo.register['time'], metazoo.register['kills']), flush=True)
        print('''
Attentiation! In this experiment, we periodically kill and reboot servers.
Some exceptions will appear in your terminal. Do not be alarmed.
Here we give some of the occuring errors, which are due to killing and not important:
 1. "KeeperErrorCode = ConnectionLoss for /ClientNode"
 2. "[Thread-18:QuorumCnxManager$SendWorker@559] - Failed to send last message.
     Shutting down thread. java.nio.channels.ClosedChannelException"
 3. "[LearnerHandler-/10.149.0.27:58498:LearnerHandler@444] - Unexpected exception
     causing shutdown while sock still open"

Attention! Due to the large amount of clients constantly reading and writing data,
snapshots and logs grow quickly to terrabyte-scale. Due to storage quota,
we periodically remove old logs and snapshots.
Happy experimenting!
''')

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        sleep_time = metazoo.register['time']
        time.sleep(sleep_time) #Client remains active for a while
        metazoo.executor.stop()


    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        nap_time = metazoo.register['time'] / (metazoo.register['nr_kills']+1)
        kills = metazoo.register['kills']
        time.sleep(nap_time)

        for kill in kills:
            if kill == metazoo.gid:
               metazoo.executor.reboot()
            time.sleep(nap_time)


    def post_experiment(self, metazoo):
        print('Experiments are done')