# Code in this file is executed on each server.
# The goal is to boot a zookeeper server, and make sure it knows of the other ones

import os
import socket
import time

import util.fs as fs
import util.location as loc
from remote.executor import Executor
from remote.config import ServerConfig

def nodenr_to_infiniband(nodenr):
    return '10.149.1.'+str(nodenr)[1:]

def prepare_classpath_symlinks():
    locations = [
        fs.join(loc.get_build_lib_dir(), 'log4j-1.2.15.jar'),
        fs.join(loc.get_build_dir(), 'zookeeper-3.3.0.jar')
    ]

    fs.mkdir(fs.join(loc.get_metazoo_dep_dir(), 'example_client'), exist_ok=True)
    for path in locations:
        dst = fs.join(loc.get_metazoo_dep_dir(), 'example_client', fs.basename(path))
        if not fs.exists(dst):
            fs.ln(path, dst)


# Starts Zookeeper, returns immediately after starting a thread containing our process
def boot(config):
    prepare_classpath_symlinks()
    command = 'java -jar {} {}'.format(fs.join(loc.get_metazoo_dep_dir(), 'example_client', 'zookeeper-client.jar'), config.hosts[0])
    executor = Executor(command)
    executor.run(shell=True)
    return executor


# Stops Zookeeper instance
def stop(executor):
    return executor.stop()
