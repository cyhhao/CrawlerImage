# coding:utf-8
import json


class Queue(list):
    def __init__(self, save_path=None):
        super(Queue, self).__init__()
        self.push_count = 0
        self.save_path = save_path
        self.isLock = False

    def empty(self):
        if self.isLock or len(self) == 0:
            return True
        else:
            return False

    def lock(self, flag):
        self.isLock = flag

    def push(self, item):
        # if self.isLock:
        #     pass
        # else:
        self.insert(0, item)
        self.push_count += 1
        if self.push_count > 50:
            self.push_count = 0
            self.save()

    def __len__(self):
        if self.isLock:
            return 0
        else:
            return super(Queue, self).__len__()

    def size(self):
        return len(self)

    def save(self):
        print 'Queue save ing...'
        with open(self.save_path, 'w') as f:
            f.write(json.dumps(self))

    def clear(self):
        del self[:]

    def pop(self, index=None):
        return super(Queue, self).pop()

    # def __del__(self):
    #     print 'del queue'
    #     self.save()

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            q = Queue(json.loads(f.read()))
            q.save_path = path
            return q
