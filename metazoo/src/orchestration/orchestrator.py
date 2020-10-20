class Orchestrator(object):
    '''Generic object to subscribe and dispatch events'''
    def __init__(self):
        self.hooks = dict()

    def add_hook(self, event, hook):
        try:
            self.hooks[event].append(hook)
        except Exception as e:
            self.hooks[event] = [hook]
    
    def execute(self, event):
        hook() for hook in self.hooks[event]

# Import this instance to use as a globally available object
instance = Orchestrator()