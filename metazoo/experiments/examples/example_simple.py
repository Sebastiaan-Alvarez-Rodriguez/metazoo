from experiments.interface import ExperimentInterface

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
        return 2

    def servers_use_infiniband(self):
        '''True if servers must communicate with eachother over infiniband, False otherwise'''
        return False

    def clients_use_infiniband(self):
        '''True if clients must communicate with servers over infinband, False otherwise'''
        return False


    def pre_experiment(self, metazoo):
        '''Execution before experiment starts. Executed on the remote once.'''
        print('Hi there! I am executed before the experiment starts!')
        metazoo.register['a_key'] = 'Hello World'
        metazoo.register['secret'] = 42
        if metazoo.id == None:
            print('I cannot use id here yet!')

    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        print('Hello from client with id={}.'.format(metazoo.id))
        time.sleep(5)
        print('I (client {}) slept well. Pre-experiment says "{}" with secret code {}. Goodbye!'.format(
            metazoo.id,
            metazoo.register['a_key'],
            metazoo.register['secret']))


    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        print('I am server {}, and I will try to modify the register now'.format(metazoo.id))
        try:
            metazoo.register['secret'] = -1
        except Exception as e:
            print('Turns out I (server {}) cannot add or change or delete variables after pre_experiment. Goodbye!'.format(metazoo.id))


    def post_experiment(self, metazoo):
        '''get amount of client nodes to allocate'''

        print('Experiments are done. Pre-experiment had this secret: {}'.format(metazoo.register['secret']))