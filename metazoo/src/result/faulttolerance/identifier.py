import util.fs as fs

class Identifier(object):
    """docstring for Identifier"""
    def __init__(self, path):
        if not fs.isfile(path):
            raise RuntimeError('Cannot read kills logs from path "{}"'.format(path))
        self._path = path

    def identify_leaders(self):
        with open(self._path, 'r') as file:
            return [line.rstrip().split(',')[2] == 'True' for line in file.readlines()]
        