import socket
import time

import util.fs as fs
import util.location as loc


class Syncer(object):
    """docstring for Syncer"""
    def __init__(self, config, experiment, designation, debug_mode=False):
        self.gid = config.gid
        self.designation = designation
        self.debug_mode = debug_mode

        self.prime = self.gid == 0 and self.designation == 'server'
        # Server 0 opens socket to listen
        if self.prime:
            self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serveraddr = (socket.gethostname(), 5000)
            self.serversock.bind(serveraddr)
            self.serversock.listen(1070) #Get up to 1070 connections before refusing them
            self.expected_connections = experiment.num_servers-1+experiment.num_clients
            self.connections = []
            if self.debug_mode: print('PRIME stage 0! Address in use: {}'.format(serveraddr), flush=True)
            for x in range(self.expected_connections):
                connection, address = self.serversock.accept()
                self.connections.append(connection)
            if self.debug_mode: print('PRIME Got all {} connections'.format(self.expected_connections), flush=True)
        else: #Others open a socket to server 0
            time.sleep(5) #Give prime a head start
            if self.designation == 'client':
                addr = (config.hosts[0].split(':')[0], 5000)
            else:
                addr = ('node{:03d}'.format(config.nodes[0]), 5000)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.debug_mode: print('{}.{} CONNECTING TO addr: {}'.format(self.designation, self.gid, addr), flush=True)
            self.sock.connect(addr)


    def _handle_sync_prime(self):
        if self.debug_mode: print('SYNC stage 1!', flush=True)
        for idx, conn in enumerate(self.connections):
            msg = conn.recv(2)
    
        if self.debug_mode: print('SYNC stage 2!', flush=True)
        # When arriving here, all expected servers and clients are connected and waiting for a reply
        for conn in self.connections:
            conn.sendall(b'go')

        if self.debug_mode: print('SYNC completed!', flush=True)


    def _handle_sync_other(self):
        try:
            self.sock.sendall(b'go')
            msg = self.sock.recv(2)
        except Exception as e:
            self.sock.close()
            raise e            


    def sync(self):
        if self.prime:
            self._handle_sync_prime()
        else:
            self._handle_sync_other()


    def close(self):
        if self.prime:
            self.serversock.close()
            # Quickly close connections and be done with it
            for conn in self.connections:
                conn.close()
        else:
            self.sock.close()

# 2-way simple syncing using sockets.
# Warning: This requires num_servers+num_clients-1 sockets open at the same time
# That means: We can deal with at most 1180 nodes in total.
# If we go over that, we will start using ports used by zookeeper
