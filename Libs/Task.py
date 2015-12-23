# coding=utf-8
from gevent import sleep
from gevent.pool import Pool
from Libs.Queue import Queue


class Task:
    def __init__(self, queue, pool_max=100):
        self.work = None
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
            elif self.pool.free_count() == self.pool.size or self.queue.isLock:
                # print 'queue is empty'
                # print self.pool.free_count(), self.pool.size
                break
            else:
                # print 'queue is empty but...'
                sleep(0)

    def stop(self):
        # 只让进队列，不让出队列
        self.queue.lock(True)
        for item in self.pool:
            self.queue.push(list(item.args))
            # print item
            # self.pool.killone(item)

        # self.pool.kill()
        # print '开始 stop的save'
        self.queue.save()
        self.queue.clear()
        # self.pool.kill()
