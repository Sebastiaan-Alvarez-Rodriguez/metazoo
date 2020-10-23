# Code in this file is executed on each client.
# The goal is to boot a zookeeper client, 
# and make sure it knows the address of the host to connect to

import os
import socket
import time

from remote.config import ServerConfig
import remote.util.ip as ip
import util.fs as fs
import util.location as loc
from util.executor import Executor


# Starts Zookeeper client, returns immediately after starting a thread containing our process
def boot(config, experiment, repeat):
    command = experiment.get_client_run_command(config, repeat)
    
    executor = Executor(command)
    executor.run(shell=True)
    return executor


# Stops Zookeeper instance
def stop(executor):
    return executor.stop()
