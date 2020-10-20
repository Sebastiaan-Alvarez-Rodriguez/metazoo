import util.fs as fs

class Reader(object):
    '''Object to read killthroughput data from a path'''
    def __init__(self, path):
        if not fs.isdir(path):
            raise RuntimeError('Cannot read killthroughput from path "{}"'.format(path))
        # Match all files with name '<number>.log', store as full path
        self.files = [x for x in fs.ls(path, only_files=True, full_paths=True) if x.endswith('.log') and fs.basename(x).split('.')[-2].isnumeric()]
        # Sort filelist on client global numbers
        self.files.sort(key=lambda x: int(fs.basename(x).split('.')[-2]))


    # Lazily read and return operations as they are needed
    def read_ops(self, client_id):
        with open(self.files[client_id], 'r') as file:
            return (int(line[5:]) for line in file.readlines())

    @property
    def num_files(self):
        return len(self.files)