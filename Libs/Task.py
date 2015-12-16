from gevent import sleep
from gevent.pool import Pool


class Task():
    def __init__(self, queue, pool_max=100):
        self.pool_max = pool_max
        self.pool = Pool(pool_max)
        self.queue = queue

    def initTaskWork(self, func):
        self.work = func

    def start(self):
        while True:
            if not self.queue.empty():
                t = self.queue.pop()
                self.pool.spawn(self.work, *t)
            elif self.pool.free_count() == self.pool.size:
                # print self.pool.free_count(), self.pool.size
                break
            else:
                sleep(0)
