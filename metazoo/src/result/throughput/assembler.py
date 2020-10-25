from result.throughput.reader import Reader
import util.fs as fs

class Assembler(object):
    def __init__(self, path):
        if not fs.isdir(path):
            raise RuntimeError('Cannot read logs from path "{}"'.format(path))
        if not fs.isdir(fs.join(path, 0)):
            raise RuntimeError('Did not find experiments in given path "{}"'.format(path))
        self._path = path

    def read_ops(self):
        for run in fs.ls(self._path, only_dirs=True, full_paths=True):
            reader = Reader(run)
            yield ((x[0][0], sum(n for _, n in x)) for x in zip(*[reader.read_ops(x) for x in range(reader.num_files)]))
