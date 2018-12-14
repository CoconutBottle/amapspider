# -*- coding:UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os
curUrl = os.path.dirname(__file__)
parUrl = os.path.abspath(os.path.join(curUrl, os.pardir))
sys.path.append(parUrl)

from settings import IsDebug
import redis


redis253 = "redis://10.1.0.253:6400/2"
redis14  = "redis://10.0.0.14:6400/2"

redisCli = redis253 if IsDebug else redis14

redis_pool= redis.ConnectionPool(max_connections=100).from_url(url=redisCli)
redconn   = redis.StrictRedis(connection_pool=redis_pool)




if __name__ == '__main__':
    print redis_url

