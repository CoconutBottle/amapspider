#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
import redis
from settings import RedisHost


class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, namespace, name ):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db= redis.from_url("redis://{}:{}/{}".format(RedisHost['host'],
                                                            RedisHost['port'],
                                                            RedisHost['db']))
        self.key = '%s:%s' %(namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item, namespace=""):
        """Put item into the queue."""
        nam = self.key if namespace == "" else namespace
        self.__db.rpush(nam, item)

    def get(self, block=True, timeout=None, namespace=""):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block

        if necessary until an item is available."""

        nam = self.key if namespace == "" else namespace
        if block:
            item = self.__db.blpop(nam, timeout=timeout)
        else:
            item = self.__db.lpop(nam)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(block=False)