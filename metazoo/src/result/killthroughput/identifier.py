import util.fs as fs

def get_kill_logs(logpath):
    return fs.join(logpath, 'experiment_logs', 'kills.log')

class Identifier(object):
    """docstring for Identifier"""
    def __init__(self, path):
        kill_logs = get_kill_logs(path)
        if not fs.isfile(kill_logs):
            raise RuntimeError('Cannot read kills logs from path "{}"'.format(path))
        self._path = path

    def identify_leaders(self):
        with open(self._path, 'r') as file:
            return (bool(line[2]) for line in file.readlines().split(','))
        