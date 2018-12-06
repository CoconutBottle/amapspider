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

# Mysql 链接
from middles.middleAssist import DBsession


### e.g. crawl_platid_objid
DEFAULT_SSDB_KEY = "crawl_{}_{}"
node_dict = {
    "单日票房":(0,1,),
}

obj_dict = {
    1:"单日票房:趋势分析",
    0:"单日票房:单日票房",
}


class YienTubes(BaseTubes):
    def __init__(self):
        super(YienTubes, self).__init__()
        self.obj = Yien()
        self.ssdb_conn  =  ssdbAssist.SSDBsession().connect()
        self.mysql_conn = DBsession.Msession()
        self.redis_conn = redisAsisst.imredis().connection()

    def tubes_detail(self, code):
        gt = self.obj.parseSingleday(self.obj.start_urls[1])
        for i in gt:
            print(i)

if __name__ == '__main__':
    p = YienTubes()
    p.tubes_detail(1)