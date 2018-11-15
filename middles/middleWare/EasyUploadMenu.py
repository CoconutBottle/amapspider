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
from middles.middleAssist import mysqlAssist

seriesId = 0
treeId = 1
class uploadMenu(object):
    def __init__(self,conn, plat, channel):
        self.conn = conn
        self.plat = plat
        self.channel = channel

        self._Rconn = redisAsisst.imredis().connection()



    def MagicTree(self, obj):
        objname = obj['objname']
        nodes    = objname.split(":")
        channel = self.channel
        setname = "plat{}:ctree:{}".format(self.plat, channel)
        for i, n in enumerate(nodes[:-1]):
            valuename = "plat{}:{}:{}".format(self.plat,channel, n)
            self._Rconn.sadd(setname,valuename)
            setname = valuename
            channel = n

        self._Rconn.sadd("plat{}:{}:{}".format(self.plat,nodes[-3],nodes[-2]),
                         objname)

    def MagicObj(self,obj , param):
        global seriesId
        print(obj)
        pinyincode = "%05d"%seriesId
        seriesId += 1
        code = "%d%s"%(param['mode']['mode'], pinyincode)
        mid = self.conn.insert(
            tbName = "t_ext_data_obj",
            plat_id = self.plat,
            code = code,
            channel_code = "YicheCrawl",
            name = obj['objname'],
            unit = obj['unit'],
            frequence_mode = obj['freq'],
            ext = str(param)
        )

        self._SlowLoadNode(mid=mid, data=obj['data'])

    def _SlowLoadNode(self, mid, data={}):
        data = data.items()
        sql  = "INSERT IGNORE INTO `t_ext_data_node` (`obj_id`, `time_t`, `amo`) VALUES ({}, %s, %s)"
        sql  = sql.format(mid)
        self.conn.executemany(sql=sql, params=data)

    def loadTree(self, node="plat{}:ctree*", seriesId=0):
        import re
        global treeId
        roots = self._Rconn.keys(node.format(self.plat))

        if not roots :
            print("eb")
        for seed in roots:

            for  nod in self._Rconn.smembers(seed):
                trId = "YC%05d"%treeId
                treeId += 1
                print(nod, trId, seriesId)
                if re.search("plat", nod):
                    print("it's node")
                    name = nod.split(":")[-1]
                else:
                    print("it's obj")
                    name = nod
                self.conn.insert(
                             tbName="t_ext_plat_menu",
                             name = name,
                             channel_code = pinyin.get(self.channel, format="strip"),
                             code = trId,plat_id = self.plat,
                             p_code = seriesId)
                self.loadTree(node=nod, seriesId=trId)

    def __del__(self):
        self.loadTree()
        self._Rconn.flushdb()




if __name__ == '__main__':
    ss = mysqlAssist.immysql()
    p = uploadMenu(conn=ss,plat=5,channel="ttest")
    p.MagicTree({"objname":"dd:11:14:13"})


