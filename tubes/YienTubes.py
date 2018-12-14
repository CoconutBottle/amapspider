#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl  = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseTubes import BaseTubes
from spiders.YienSpider import Yien
from middles.middleAssist import mysqlAssist, ssdbAssist, redisAsisst

from gevent import monkey
import gevent

import pinyin

# Mysql 链接
#from middles.middleAssist import DBsession
from slaver import  YienSlaver

### e.g. crawl_platid_objid
DEFAULT_SSDB_KEY = "crawl_{}_{}_{}"
node_dict = {
    "单日票房":(0,1,),
}

obj_dict = {
    1:"单日票房:趋势分析",
    0:"单日票房:单日票房",
}
channel_dict ={
0:'单日票房',1:'单日趋势分析',
2:'单周票房',3:'周末票房',
4:'单月票房',5:'年度票房',
6:'年度首周票房',7:'影院票房',
}

ssdb_conn  =  ssdbAssist.SSDBsession().connect()
mysql_conn = mysqlAssist.immysql()
redis_conn = redisAsisst.imredis().connection()

class YienTubes(BaseTubes):
    def __init__(self):
        super(YienTubes, self).__init__()
        self.obj = Yien()

        self.plat_id = 8
        self.channel = ("yiendata", "艺恩数据")


    def tubes_detail(self, code):
        cod = code
        gt = self.obj.parse(cod)
        for i in gt:
            print(i['moviename'])
            mysql_conn.insert(tbName="t_ext_seed_data",
                                   platform="yien",
                                   seed_val= i['moviename'],
                                   pseed = cod,
                                   note = i['code'],
                                   seed = i['obj'],
                                   gId=1)

            print(i['time_t'])
            SSDB_KEY = DEFAULT_SSDB_KEY.format(self.plat_id, cod, i['obj'])
            print(SSDB_KEY)
            ssdb_conn.hset(SSDB_KEY,i["time_t"], i['value'])

    def tubesChannelNodeObj(self, mode, ep):
        is_loop = True
        sql = "SELECT pseed, seed ,seed_val,note  FROM t_ext_seed_data " \
              "WHERE platform = 'yien' AND pseed={} LIMIT %s, 500".format(mode)
        print(sql)
        i, result = 0, mysql_conn.query(sql % 0)
        print(result)
        while is_loop:
            if not result:break
            for k, tt in enumerate(result):
                for i in YienSlaver.Ripper(ssdbconn=ssdb_conn, tid=tt[1], mode=tt[0]):
                    i['objname'] = "艺恩##%s##%s##%s"%(channel_dict[int(tt[0])],
                                                    i['objname'], tt[2])
                    print(i['objname'])
                    i['data'] = dict(i['data'])
                    i['unit'] = ""
                    i['freq'] = 3
                    i['mode'] = {"mode":"e","ext":i['ext'],"ID":tt[1]}
                    ep.loadSQL(i)
            i += 500

def updateObj():
    monkey.patch_all()
    import json
    from middles.middleWare import  EasyUploadMenu

    p = YienTubes()


    # gt = [gevent.spawn(p.tubes_detail, i) for i in range(8)]
    # gevent.joinall(gt)

    ep = EasyUploadMenu.uploadMenuQueue(conn=mysql_conn,plat=8,channel="Yien",
                                        prefix='YE')
    ep.setChannelCode(name="yiencode")


    # gt = [gevent.spawn(p.tubesChannelNodeObj, i, ep) for i in range(0, 8)]
    # gevent.joinall(gt)

    del ep

def getObjData():
    from middles.middleWare import fakeQueue
    qname = "tmpCollectDATAqueue"
    queue = fakeQueue.RedisQueue(qname, "8")
    while True:
        try:
            data = eval(queue.get(timeout=30))
            yield data
        except:
            yield -1




if __name__ == '__main__':
    for i in getObjData():
        print(i)
