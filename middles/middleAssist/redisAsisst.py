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


class imredis(object):
    def __init__(self):
        self.host = RedisHost["host"]
        self.port = RedisHost["port"]
        self.pw = RedisHost["passwd"]
        self.db = RedisHost["db"]

    def setVar(self, host="127.0.0.1", port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def connection(self):
        return redis.Redis(host=self.host,
                           port=self.port,
                           password=self.pw,
                           db=self.db)

    def __del__(self):
        del self


def initAccount():
    from middles.middleAssist import  ssdbAssist
    from middles.middleWare import  EasyMethod
    t = ssdbAssist.SshSSDB().connect()
    n = eval(t.get("robo:uname"))

    # n = ['zzm','com', 'cwf', 'fwb','llb']
    # t = imredis().connection()
    for i in n:
        EasyMethod.RoboEasyLogin(i,2)

if __name__ == '__main__':
    initAccount()
