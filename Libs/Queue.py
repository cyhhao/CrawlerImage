# coding:utf-8
class Queue(list):
    def __init__(self):
        super(Queue, self).__init__()

    def empty(self):
        if len(self) == 0:
            return True
        else:
            return False

    def push(self, item):
        self.insert(0, item)

    def size(self):
        print len(self)
