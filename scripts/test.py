#!/usr/bin/python

import socket
import os
print('Hola from node '+socket.gethostname()+'!')
print('my IP is: '+socket.gethostbyname(socket.gethostname()))

def printenvs(keys):
    for key in keys:
        try:
            print('{0:12}  {1}'.format(key.lower(), os.environ[key]))
        except KeyError as e:
            print('{0:12}  UNAVAILABLE KEY'.format(key.lower()))

fellow_nodes = os.environ['HOSTS'].split()
fellow_nodes.remove(socket.gethostname())
print('My fellow nodes are: ', end='')
print(*fellow_nodes)
print('Their IPs are: ', end='')
for x in fellow_nodes:
    print('{} (host: {})'.format(socket.gethostbyname(x), x), end=' ')

print('')
#useful_envvars = ['SSH_CLIENT', 'SLURM_NTASKS', 'SLURM_NNODES', 'HOSTS', 'SLURM_JOB_NODELIST', 'SSH_CONNECTION', 'SLURMD_NODENAME', 'PANDA_HOST_PORT_KEY']
useful_envvars = ['SLURM_JOB_NODELIST', 'SLURMD_NODENAME', 'SLURM_NODEID', 'SLURM_PROCID', 'SLURM_LOCALID', 'SLURM_NPROCS', 'SLURM_NTASKS', 'SLURM_NNODES', 'SLURM_TASKS_PER_NODE', 'PRUN_CPU_RANK', 'SLURM_GTIDS', 'HOSTS', 'PRUN_HOSTNAMES']
# printenvs(os.environ)
printenvs(useful_envvars)

print('\n\n')
# SLURM_NTASKS
# SLURM_NNODES
# 'HOSTS': 'node112 node113 
# 'SLURM_JOB_NODELIST': 'node[112-113]'
# 'SSH_CONNECTION': '132.229.44.36 58136 132.229.137.11 22'
# 'SLURMD_NODENAME': 'node112'
