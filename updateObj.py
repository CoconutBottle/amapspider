#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)


from tubes import YienTubes

import gevent
from gevent import monkey
import redis_Queue
p = YienTubes.YienTubes()
queue = redis_Queue.RedisQueue("Rqueue", "uPdateObjQueue")
FailQueue = "Rqueue:uPdateObjFail"
SuccQueue = "Rqueue:uPdateObjSucc"


def worker(info):
    import datetime
    try:
        gt = [gevent.spawn(p.tubes_detail, i) for i in range(8)]

        gevent.joinall(gt)

        gt = [gevent.spawn(p.tubesChanelNodeObj, i) for i in range(8)]
        gevent.joinall(gt)
    except Exception as e:
        info['error'] = e
        info['report']= datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        queue.put(item=info, namespace=FailQueue)
    else:
        info['report']= datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        queue.put(item=info, namespace=SuccQueue)

if __name__ == '__main__':
    while True:
        info = queue.get(timeout=30)
