import json


class UrlSet(dict):
    def __init__(self, save_path=None):
        self.save_path = save_path
        super(UrlSet, self).__init__()

    def save(self):
        print 'Queue save ing...'
        with open(self.save_path, 'w') as f:
            f.write(json.dumps(self))

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            set=UrlSet(json.loads(f.read()))
            set.save_path=path
            return set
