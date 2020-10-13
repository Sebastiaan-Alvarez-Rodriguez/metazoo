import pickle

import util.fs as fs
import util.location as loc


class MetaZoo(object):
    def __init__(self):
        self.register = dict()
        self.log = None
        self._id = None


    @property
    def id(self):
        return self._id
    

    # Function to completely prohibit changing (i.e. writing, updating, deleting) MetaZoo register
    def lock():
        def __readonly__(self, *args, **kwargs):
            raise RuntimeError('Cannot change MetaZoo register past the pre_experiment stage')
        self.register.__setitem__ = __readonly__
        self.register.__delitem__ = __readonly__
        self.register.pop = __readonly__
        self.register.popitem = __readonly__
        self.register.clear = __readonly__
        self.register.update = __readonly__
        self.register.setdefault = __readonly__
        del __readonly__


    # Function to persist this instance using pickling
    def persist(self):
        with open(fs.join(loc.get_remote_prj_dir(), '.hidden.persist.pickle'), 'wb') as file:
            try:
                pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                print('[FAILURE] Could not persist register. Did you store any Objects that cannot be pickled in the MetaZoo register?')
                raise e


    # Function to load persisted object using pickling
    @staticmethod
    def load():
        location = fs.join(loc.get_remote_prj_dir(), '.hidden.persist.pickle')
        if not fs.isfile(location):
            raise RuntimeError('Temporary state file not found at {}'.format(location))
        with open(location, 'rb') as file:
            try:
                return pickle.load(file)
            except Exception as e:
                print('[FAILURE] Could not load register. Did you store any Objects that cannot be pickled in the MetaZoo register?')
                raise e


    @staticmethod
    def clean():
        fs.rm(fs.join(loc.get_remote_prj_dir(), '.hidden.persist.pickle'), ignore_errors=True)