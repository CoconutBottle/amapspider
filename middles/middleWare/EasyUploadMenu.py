#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl  = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
import pinyin
from middles.middleAssist import ssdbAssist
from middles.middleAssist import redisAsisst

seriesId = 0

class uploadMenu(object):
    def __init__(self,conn, plat, channel):
        self.conn = conn
        self.plat = plat
        self.channel = channel
        self._Rconn = redisAsisst.imredis().connection()



    def lubricateMenu(self, obj):
        objname = obj['objname']
        nodes    = objname.split(":")
        setname = "plat{}:ctree:{}".format(self.plat, self.channel)
        print(objname)
        print(nodes)
        d = []
        for i, n in enumerate(nodes[:-1]):

            self._Rconn.sadd("node:%s:%s"%(self.channel,n),"node:%s_%s"%(self.channel,n))
            self.channel = n

        self._Rconn.sadd("obj:%s:%s"%(self.channel,nodes[-1]),
                         "%s:%s"%(self.channel, objname[-1]))

    def lubricateObj(self,obj):
        global seriesId
        print(obj)
        pinyincode = "%05d"%seriesId
        seriesId += 1
        code = "%d%s"%(obj['mode']['mode'], pinyincode)
        self.conn.insert(
            tbName = "t_ext_data_obj",
            plat_id = self.plat,
            code = code,
            channel_code = "YicheCrawl",
            name = obj['objname'],
            unit = obj['unit'],
            frequence_mode = obj['freq'],
            ext = str(obj['mode'])
        )





if __name__ == '__main__':
    p = uploadMenu(1,5,"test")
    p.lubricate({"objname":"d:b:d:e"})