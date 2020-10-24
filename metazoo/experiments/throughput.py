class ThroughputExperiment(ExperimentInterface):
    '''
    Experiment measuring throughput performance of saturated servers
    as server nodes get killed
    '''
    def num_servers(self):
        '''Get amount of server nodes to allocate'''
        return 13

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
        return 8

    def server_periodic_clean(self):
        '''Period in seconds for servers to clean their crawlspaces. 0 means no cleaning'''
        return 8


    # Constructs symlinks in zookeeper-client directory, so classpath resolves to required jars 
    def _prepare_classpath_symlinks(self):
        locations = [
            fs.join(loc.get_build_lib_dir(), 'log4j-1.2.15.jar'),
            fs.join(loc.get_build_dir(), 'zookeeper-3.3.0.jar'),
        ]

        fs.mkdir(fs.join(loc.get_metazoo_dep_dir(), 'throughput_client'), exist_ok=True)
        for path in locations:
            dst = fs.join(loc.get_metazoo_dep_dir(), 'throughput_client', fs.basename(path))
            if not fs.exists(dst):
                fs.ln(path, dst)


    def pre_experiment(self, metazoo):
        self._prepare_classpath_symlinks()
        '''Execution before experiment starts. Executed on the remote once.'''
        metazoo.register['time'] = 5
        print('''
Attention! Due to the large amount of clients constantly reading and writing data,
snapshots and logs grow quickly to terrabyte-scale. Due to storage quota,
we periodically remove old logs and snapshots.
Happy experimenting!
''')

    def get_client_run_command(self, metazoo):
        '''Get client run command, executed in All client nodes'''
        return 'java -Dlog4j.configuration=file:"{}" "-Dprops={}" -jar {} {} {} {}'.format(
        fs.join(loc.get_client_cfg_dir(), 'log4j.properties'),
        'ERROR, CONSOLE',
        fs.join(loc.get_metazoo_dep_dir(), 'throughput_client', 'zookeeper-client.jar'),
        balancer.balance_simple(metazoo.hosts, metazoo.gid),
        metazoo.gid,
        fs.join(loc.get_node_log_dir(), '{}.log'.format(metazoo.gid)))


    def experiment_client(self, metazoo):
        '''Execution occuring on ALL client nodes'''
        sleep_time = metazoo.register['time']
        time.sleep(sleep_time) #Client remains active for a while
        metazoo.executor.stop()

    def experiment_server(self, metazoo):
        '''Execution occuring on ALL server nodes'''
        sleep_time = metazoo.register['time']
        time.sleep(sleep_time)

    def post_experiment(self, metazoo):
        print('Experiments are done')