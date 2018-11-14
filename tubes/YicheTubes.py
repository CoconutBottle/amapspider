#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl  = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseTubes import BaseTubes
from spiders.YicheSpider import Yiche

from middles.middleAssist import mysqlAssist
from middles.middleWare import EasyMethod, EasyUploadMenu
from middles.middleAssist import logAsisst
logname = 'test'

class YicheTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,**kwargs):
        global logname
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self.obj = Yiche()
        self._Mconn = mysqlAssist.immysql()

        #self.Logger = logAsisst.imLog(logname)()

    def tubes_detail(self, code, **kwargs):

        ## 2,1,0
        if not isinstance(code, int): raise ValueError("Code 必须是整数")
        if code in (0,1,2):
            for i in self.obj.parseMarketMonth(self.obj.obj_urls[code]):
                try:
                    i["mode"] = {"mode":code}
                    yield i
                except Exception as e:
                    print(e)
        ## 3, 4 type 0
        ## 5, 6 type 1
        elif code in (3,4,5,6):
            type = 0 if code < 5 else 1
            for m in (0,2,3):
                for i in self.obj.parseMarketSeason(self.obj.obj_urls[code],
                                                    mod=m, type=type):
                    try:
                        i["mode"] = {"mode":code,"mod":m,"type":type}
                        yield i
                    except Exception as e:print(e)

        elif code == 7 or code == 8:
            sql = """
                SELECT a.channel_code, a.name, a.code FROM t_ext_plat_menu a
                INNER JOIN t_ext_seed_data b ON b.seed = a.`code`
                WHERE a.plat_id = 5 AND b.`level` = 0
            """
            for tt in self._Mconn.query(sql):
                name, cde = tt[1], tt[-1]
                t = self.obj.parseRank(code = cde, name= name)
                try:
                    for i in t:
                        i["mode"] = {"mode":code,"name":name,"code":cde}
                        yield i
                except Exception as e:
                    print(e)

        elif code ==9:
            sql = """
                SELECT seed, seed_val FROM t_ext_seed_data WHERE level =1 
            """
            for tt in self._Mconn.query(sql):
                name, cde = tt[1], tt[0]
                t = self.obj.parseSales(pid=4, code = cde, name="易车指数:排行榜:销量:" + name)
                try:
                    for i in t:
                        i["mode"] = {"mode":code,"name":name,"code":cde}
                        yield i
                except Exception as e:
                    print(e)
        else:
            raise ValueError("code 取值只能是0~9")

    def rConn(self, mode='M'):
        return self._Mconn

if __name__ == '__main__':
    p = YicheTubes()
    ep = EasyUploadMenu.uploadMenu(conn=p.rConn(), plat=5, channel="YicheCrawl")
    for k in range(10):
        for i in p.tubes_detail(k):
            ep.lubricateObj(i)