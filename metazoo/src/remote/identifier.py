import os
import socket
from math import ceil

def num_nodes():
    return int(os.environ['SLURM_NNODES'])

# Gives max number of processes per node (e.g. returns 2 if we have 2 servers and 1 client)
# Note: Should return 1 if we have 1 server and 2 clients
# def num_procs_per_node():
#     return ceil(int(os.environ['SLURM_NPROCS']) / num_nodes())
def num_procs_per_node():
    return int(os.environ['SLURM_NPROCS']) // num_nodes()


def __sanity_check(rank):
    host = socket.gethostname()
    # node117   node117   node118   node118   node119   node119
    nodenames = os.environ['HOSTS'].split()
    # node117/0 node117/1 node118/0 node118/1 node119/0 node119/1
    # prun_nodenames = os.environ['PRUN_HOSTNAMES'].split()
    # 0         1         2         3         4         5
    expected_rankings = [x for x in range(len(nodenames))]
    # 2
    expected_rank_min = nodenames.index(host)
    # 3
    # expected_rank_max = len(nodenames)-1-nodenames[::-1].index(host)
    expected_rank_max = expected_rank_min-1+num_procs_per_node()
    if rank < expected_rank_min or rank > expected_rank_max:
        raise RuntimeError('Sanity check failed! Expected host {} to have rank in [{}, {}], but found: {}'.format(host, expected_rank_min, expected_rank_max, rank))
    

# Gives a global id, i.e: Different for every process
def identifier_global():
    rank = int(os.environ['PRUN_CPU_RANK'])
    __sanity_check(rank)
    return rank

# Gives a local id, i.e: Different between processes on the same node, but potentially equivalent between 2 or more processes
def identifier_local():
    # node118 (suppose we are node118/1)
    host = socket.gethostname()
    # node117   node117   node118   node118   node119   node119
    nodenames = os.environ['HOSTS'].split()
    # node117/0 node117/1 node118/0 node118/1 node119/0 node119/1
    # prun_nodenames = os.environ['PRUN_HOSTNAMES'].split()
    # 0         1         2         3         4         5
    expected_rankings = [x for x in range(len(nodenames))]
    # 2
    expected_rank_min = nodenames.index(host)
    # 3
    # expected_rank_max = len(nodenames)-1-nodenames[::-1].index(host)
    expected_rank_max = expected_rank_min-1+num_procs_per_node()
    # 3
    rank = identifier_global()
    # 1
    local_rank = rank - expected_rank_min
    return local_rank
'''
End goal:
server.0=<ip1>:2182:2183 #share node1
server.1=<ip1>:2184:2185 #share node1
server.2=<ip2>:2182:2183 #share node2
server.3=<ip2>:2184:2185 #share node2
''' 