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
from middles.middleWare import fakeQueue
import hashlib

SSDB_DEFAULT_KEY = "s_o_d_i_{}"

seriesId = 0
treeId = 1
_SSDB = ssdbAssist.SSDBsession()
_Rconn = redisAsisst.imredis().connection()


def str2md5(s, p=8):
    md = hashlib.md5(s)
    a = md.hexdigest()[:p]
    return a

NodeDATAQueue="tmpCollectDATAqueue"


class uploadMenu(object):
    def __init__(self,conn, plat, channel, prefix="YC"):
        self.conn = conn
        self.plat = plat
        self.channel = channel
        if int(plat) == 8 : self.p = 8
        else:self.p = 10
        self.channel_code = "YicheCrawl"
        self.prefix = prefix

    def setChannelCode(self, name):
        import re
        if re.search("[^0-9a-zA-Z]", name):
            raise ValueError("name 只可以为字母数字")
        print(name)
        self.channel_code = name


    def MagicTree(self, obj):
        objname = obj['objname']
        nodes    = objname.split("##")
        channel = self.channel
        setname = "plat{}:ctree:{}".format(self.plat, channel)
        for i, n in enumerate(nodes[:-1]):
            valuename = "plat{}:{}:{}".format(self.plat,channel, n)
            _Rconn.sadd(setname,valuename)
            setname = valuename
            channel = n


        _Rconn.sadd("plat{}:{}:{}".format(self.plat,nodes[-3],nodes[-2]),
                         objname)


    def MagicObj(self,obj , param):
        global seriesId
        print(obj)

        seriesId += 1
        print("param >>>", param['mode']['mode'])
        code = str2md5(obj['objname'])

        mid = self.conn.query("select id,plat_id from t_ext_data_obj "
                              "where plat_id=%s and code='%s'"%(self.plat, code))
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

        self._LoadNode(mid=mid, data=obj['data'])

    def _LoadNode(self, mid, data={}):
        data = data.items()
        _Rconn.sadd("SSDB:HKEYS", SSDB_DEFAULT_KEY.format(mid))

        # _SSDB.multihset(SSDB_DEFAULT_KEY.format(mid), data)
        sql  = "REPLACE INTO `t_ext_data_node` (`obj_id`, `time_t`, `amo`) VALUES ({}, %s, %s)"
        sql  = sql.format(mid)
        self.conn.executemany(sql=sql, params=data)

    def loadTree(self, node="plat{}:ctree*", seriesId=""):
        import re
        global treeId
        roots = _Rconn.keys(node.format(self.plat))

        if not roots :
            print("eb")
        for seed in roots:

            for  nod in _Rconn.smembers(seed):

                treeId += 1
                print(nod,  seriesId)
                if re.search("plat", nod):
                    print("it's node")
                    name = nod.split(":")[-1]
                else:
                    print("it's obj")
                    name = nod

                code = str2md5(name, self.p)

                self.conn.insert(
                             tbName="t_ext_plat_menu",
                             name = name,
                             channel_code = self.channel_code,
                             code = code,plat_id = self.plat,
                             p_code = seriesId)
                self.loadTree(node=nod, seriesId=code)

    def loadSQL(self, obj):
        i = obj
        p = {"mode":obj['mode']}

        self.MagicObj(obj=i, param=p)
        self.MagicTree(obj=i)



    def __del__(self):
        self.loadTree()
        map(lambda x:_Rconn.delete(x),
            _Rconn.keys("plat{}*".format(self.plat)))

        self.conn.query("insert ignore into t_ext_data_channel(plat_id,"
                        " channel_name, channel_code) values "
                        "('%s','%s','%s')"%(self.plat, self.channel, self.channel_code))

        self.conn.query(
            """UPDATE t_ext_plat_menu a 
                LEFT JOIN t_ext_data_obj b ON b.plat_id = {} AND a.name = b.name
                SET a.`code` = b.`code`, 
                a.`type` = 1 WHERE a.plat_id = {} AND a.name = b.name
            """.format(self.plat, self.plat)
        )
        print("FlushDB All KEYS -plat*")








class uploadMenuQueue(object):
    def __init__(self,conn, plat, channel, prefix="YC"):
        self.conn = conn
        self.plat = plat
        if int(plat) == 5:
            self.p = 10
        else:self.p = 8
        self.channel = channel
        self.channel_code = None
        self.prefix = prefix
        self.queue = fakeQueue.RedisQueue(NodeDATAQueue, plat)

    def setChannelCode(self, name):
        import re
        if re.search("[^0-9a-zA-Z]", name):
            raise ValueError("ChanenlCode 只可以为字母数字")
        print(name)
        self.channel_code = name


    def MagicTree(self, obj):
        objname = obj['objname']
        nodes    = objname.split("##")
        channel = self.channel
        setname = "plat{}:ctree:{}".format(self.plat, channel)
        for i, n in enumerate(nodes[:-1]):
            valuename = "plat{}:{}:{}".format(self.plat,channel, n)
            _Rconn.sadd(setname,valuename)
            setname = valuename
            channel = n


        _Rconn.sadd("plat{}:{}:{}".format(self.plat,nodes[-3],nodes[-2]),
                    objname)


    def MagicObj(self,obj , param):
        global seriesId
        print(obj)

        seriesId += 1

        code = str2md5(obj['objname'], self.p)
        self.conn.insert(
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


        self._LoadNode(self.plat, code, data=obj['data'])

    def _LoadNode(self, plat, code, data={}):

        sql = "select id,plat_id from t_ext_data_obj \
            where plat_id=%s and code='%s'"%(plat, code)
        print(sql)
        mid = self.conn.query(sql)
        try:
            mid = mid[0][0]
            obj =  {
                    "obj_id":mid,
                    "data":data
            }
            self.queue.put(obj)
        except:pass



    def loadTree(self, node="plat{}:ctree*", seriesId=""):
        import re
        global treeId
        roots = _Rconn.keys(node.format(self.plat))

        if not roots :
            print("eb")
        for seed in roots:

            for  nod in _Rconn.smembers(seed):

                treeId += 1
                print(nod,  seriesId)
                if re.search("plat", nod):
                    name = nod.split(":")[-1]
                else:
                    name = nod
                code = str2md5(name, self.p)
                self.conn.insert(
                    tbName="t_ext_plat_menu",
                    name = name,
                    channel_code = self.channel_code,
                    code = code,plat_id = self.plat,
                    p_code = seriesId)
                self.loadTree(node=nod, seriesId=code)

    def loadSQL(self, obj):
        i = obj
        p = {"mode":obj['mode']}

        self.MagicObj(obj=i, param=p)
        self.MagicTree(obj=i)



    def __del__(self):
        self.loadTree()
        map(lambda x:_Rconn.delete(x),
            _Rconn.keys("plat{}*".format(self.plat)))

        self.conn.query("insert ignore into t_ext_data_channel(plat_id,"
                        " channel_name, channel_code) values "
                        "('%s','%s','%s')"%(self.plat, self.channel, self.channel_code))

        self.conn.query(
            """UPDATE t_ext_plat_menu a 
                LEFT JOIN t_ext_data_obj b ON b.plat_id = {} AND a.name = b.name
                SET a.`code` = b.`code`, 
                a.`type` = 1 WHERE a.plat_id = {} AND a.name = b.name
            """.format(self.plat, self.plat)
        )
        print("FlushDB All KEYS -plat*")




if __name__ == '__main__':
    print(str2md5("大家好"))
