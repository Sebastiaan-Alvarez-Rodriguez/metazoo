from collections.abc import MutableMapping

class Registrar(MutableMapping):
    '''Generic key-value store to maintain useful information from hooks'''
    def __init__(self):
        self.data = dict()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

# Import this instance to have the globally available registrar available
instance = Registrar()