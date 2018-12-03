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


SSDB_DEFAULT_KEY = "s_o_d_i_{}"

seriesId = 0
treeId = 1
class uploadMenu(object):
    def __init__(self,conn, plat, channel, prefix="YC"):
        self.conn = conn
        self.plat = plat
        self.channel = channel
        self._SSDB = ssdbAssist.SSDBsession()
        self._Rconn = redisAsisst.imredis().connection()
        self.channel_code = "YicheCrawl"
        self.prefix = prefix

    def setChannelCode(self, name):
        import re
        if re.search("[^0-9a-z]", name):
            raise ValueError("name 只可以为字母数字")
        print(name)
        self.channel_code = name


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
        print("param >>>", param['mode']['mode'])
        code = "%s%s"%(param['mode']['mode'], pinyincode)
        mid = self.conn.query("select id from t_ext_data_obj "
                              "where plat_id=%s and name='%s'"%(self.plat, obj['objname']))
        try:
            mid = mid[0][0]
            if not mid:
                raise ValueError
        except:

            mid = self.conn.insert(
                tbName = "t_ext_data_obj",
                plat_id = self.plat,
                code = code,
                channel_code = self.channel_code,
                name = obj['objname'],
                data_source = self.channel,
                unit = "" if obj['unit'] is None else obj['unit'],
                frequence_mode = obj['freq'],
                ext = str(param) if not isinstance(param, str) else param
            )

        self._SlowLoadNode(mid=mid, data=obj['data'])

    def _SlowLoadNode(self, mid, data={}):

        data = data.items()
        self._Rconn.sadd("SSDB:HKEYS", SSDB_DEFAULT_KEY.format(mid))

        self._SSDB.multihset(SSDB_DEFAULT_KEY.format(mid), data)
        sql  = "REPLACE INTO `t_ext_data_node` (`obj_id`, `time_t`, `amo`) VALUES ({}, %s, %s)"
        sql  = sql.format(mid)
        self.conn.executemany(sql=sql, params=data)

    def loadTree(self, node="plat{}:ctree*", seriesId="0"):
        import re
        global treeId
        roots = self._Rconn.keys(node.format(self.plat))

        if not roots :
            print("eb")
        for seed in roots:

            for  nod in self._Rconn.smembers(seed):
                trId = "%s%05d"%(self.prefix, treeId)
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
                             channel_code = self.channel_code,
                             code = trId,plat_id = self.plat,
                             p_code = seriesId)
                self.loadTree(node=nod, seriesId=trId)

    def __del__(self):
        # self.loadTree()
        map(lambda x:self._Rconn.expire(x, 300),
            self._Rconn.keys("plat{}*".format(self.plat)))
        self.conn.query(
            """UPDATE t_ext_plat_menu a 
                LEFT JOIN t_ext_data_obj b ON b.plat_id = {} AND a.name = b.name
                SET a.`code` = b.`code`, 
                a.`type` = 1 WHERE a.plat_id = {} AND a.name = b.name
            """.format(self.plat, self.plat)
        )
        print("FlushDB All KEYS -plat*")


if __name__ == '__main__':
    ss = mysqlAssist.immysql()
    p = uploadMenu(conn=ss, plat=6, channel="ZhongTou")

    p.setChannelCode("asss")


