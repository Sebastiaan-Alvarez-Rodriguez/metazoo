import time

import util.fs as fs
import util.location as loc

'''
This file has functions to synchronise clusters with a 1-second accuracy,
and takes minimally 2
That is:
We guarantee a max timespan of 1 second between any 2 nodes after calling sync()

The syncing itself is a 3-stage process:
    server0                       | others
 0. builds sync dir               | waits for stage0 completion token
 1. announces itself              | announce themselves
 2. waits until all have anounced | wait for stage1 completion token

To make sure that syncing still works later on, stage0 token is removed
when server0 found everyone had anounced themselves.
This way, the system will not skip stages on a repeat.
'''


# 2-way simple syncing using filesystem. 
def sync(config, experiment, designation):

    # Stage 0: we build sync dir if server0, others wait until that is done
    if config.gid == 0 and designation == 'server':
        fs.rm(loc.get_metazoo_sync_dir(), ignore_errors=True) # In case of unsuccessful past runs
        fs.mkdir(loc.get_metazoo_sync_dir())
        fs.touch(loc.get_metazoo_sync_dir(), 'stage0')
        print('[SYNC] Synchronisation initiated', flush=True)
    else:
        if config.gid ==0 and designation=='client': print('CLient {} stage 5'.format(config.gid), flush=True)
        while not fs.exists(loc.get_metazoo_sync_dir(), 'stage0'):
            time.sleep(1)
        if config.gid ==0 and designation=='client': print('CLient {} stage 6'.format(config.gid), flush=True)
        

    # Stage 1: Everyone announces
    fs.touch(loc.get_metazoo_sync_dir(), '{}.{}'.format(designation, config.gid))
    print('[SYNC] {}.{} announced!'.format(designation, config.gid), flush=True)

    # Stage 2: server0 checks if everyone has announced, others wait.
    # Note: When server0 finds all have announced, removes stage0 token
    if designation == 'server' and config.gid == 0:
        while True:
            ready_nodes = [x for x in fs.ls(loc.get_metazoo_sync_dir(), only_files=True) if x.split('.')[-1].isnumeric()]
            ready_servers = set([int(x.split('.')[1]) for x in ready_nodes if fs.basename(x).split('.')[0] == 'server'])
            ready_clients = set([int(x.split('.')[1]) for x in ready_nodes if fs.basename(x).split('.')[0] == 'client'])
            diff_servers = set(range(experiment.num_servers)) - ready_servers
            diff_clients = set(range(experiment.num_clients)) - ready_clients

            if len(diff_servers) > 0 and len(diff_clients) > 0:
                print('[SYNC] Waiting on servers {} and clients {}'.format(diff_servers, diff_clients), flush=True)               
            elif len(diff_servers) > 0:
                print('[SYNC] Waiting on servers {}'.format(diff_servers), flush=True)
            elif len(diff_clients) > 0:
                print('[SYNC] Waiting on clients {}'.format(diff_clients), flush=True)
            else:
                # Everyone has announced. It is safe to remove stage0 token
                fs.rm(loc.get_metazoo_sync_dir(), 'stage0')
                fs.touch(loc.get_metazoo_sync_dir(), 'stage1') # stage1 completed!
                print('[SYNC] Sync finished!', flush=True)
                return
            time.sleep(1)
    else:
        # Wait for other nodes to sync
        while not fs.exists(loc.get_metazoo_sync_dir(), 'stage1'):
            time.sleep(1)
