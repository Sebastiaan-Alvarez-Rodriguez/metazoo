import subprocess
import os
import threading
from util.lock import Synchronized

class Executor(Synchronized):
    # Run subprocess commands in a different thread

    def __init__(self, cmd):
        self.cmd = cmd
        self.started = False
        self.stopped = False
        self.thread = None
        self.process = None



    def run(self, **kwargs):
        if self.started:
            raise RuntimeError('Executor already started. Make a new Executor for a new run')
        if self.stopped:
            raise RuntimeError('Executor already stopped. Make a new Executor for a new run')

        def target(**kwargs):
            self.process = subprocess.Popen(self.cmd, **kwargs)
            self.started = True
            self.process.communicate()
            self.stopped = True

        self.thread = threading.Thread(target=target, kwargs=kwargs)
        self.thread.start()


    def stop(self):
        if self.started and not self.stopped:
            if self.thread.is_alive():
                self.process.terminate()
                self.thread.join()
        return self.process.returncode
        # if self.started and not self.stopped:
        #     os.system('kill -9 {0}'.format(thread.get_native_id()))


    def get_pid(self):
        if (not self.started) or self.stopped or self.process == None:
            return -1
        return self.process.pid