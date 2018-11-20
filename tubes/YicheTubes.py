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
            for i, p in self.obj.parseMarketMonth(self.obj.obj_urls[code]):
                try:
                    p["mode"] = {"mode":code}
                    yield i, p
                except Exception as e:
                    print(e)
        ## 3, 4 type 0
        ## 5, 6 type 1
        elif code in (3,4,5,6):
            type = 0 if code < 5 else 1
            for m in (0,2,3):
                for i, p in self.obj.parseMarketSeason(self.obj.obj_urls[code],
                                                    mod=m, type=type):
                    try:
                        p["mode"] = {"mode":code,"mod":m,"type":type}
                        yield i, p
                    except Exception as e:print(e)

        elif code == 7 or code == 8:
            sql = """
                SELECT CONCAT('易车指数:排行榜:趋势:[', b.seed_val,']'), seed FROM t_ext_seed_data b
                WHERE  b.`level` = 0
            """
            for tt in self._Mconn.query(sql):
                name, cde = tt[0], tt[-1]
                t = self.obj.parseRank(code = cde, name= name)
                try:
                    for i, p in t:
                        p["mode"] = {"mode":code,"name":name,"code":cde}
                        yield i, p
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
                    for i, p in t:
                        p["mode"] = {"mode":code,"name":name,"code":cde}
                        yield i, p
                except Exception as e:
                    print(e)
        else:
            raise ValueError("code 取值只能是0~9")

    def rConn(self, mode='M'):
        return self._Mconn

    def ModeOption(self, mode, objname):
        import re
        mod = mode['mode']
        if mod in (0, 1, 2):
            for i, p in self.obj.parseMarketMonth(self.obj.obj_urls[mod]):
                if i['objname'] == objname:
                    return i
        elif mod in (3,4,5,6):
            type = 0 if mod < 5 else 1
            for m in (0,2,3):
                for i, p in self.obj.parseMarketSeason(self.obj.obj_urls[mod],
                                                       mod=m, type=type):
                    try:
                        if i['objname'] == objname:
                            return i
                    except Exception as e:print(e)
        elif mod == 7 or mod == 8:
            name = mode['name']
            code = mode['code']
            try:
                for i, p in self.obj.parseRank(code = code, name= name):
                    if i['objname'] == objname:
                        return i
            except Exception as e:
                print(e)
        elif mod == 9:
            name = mode['name']
            code = mode['code']
            t = self.obj.parseSales(pid=4, code = code, name="易车指数:排行榜:销量:" + name)
            try:
                for i, p in t:
                    if i['objname'] == objname:
                        return i
            except Exception as e:
                print(e)


    def Tubes(self, taskinfo):
        import datetime
        try:
            self.plat_id = taskinfo["plat_id"]
            code = eval(taskinfo["obj_ext"])
            mode = code['mode']
            dataflow = self.ModeOption(mode=mode, objname=taskinfo['objname'])
            taskinfo['report_time'] = '%s' % \
                                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            taskinfo["data"] = dataflow["data"]
            taskinfo['process_code'] = os.getpid()
            return  taskinfo

        except Exception as e:
            print(e)
            self.Logger.error(["TubesError[%d]" % os.getpid(), e])





if __name__ == '__main__':
    p = YicheTubes()
    ep = EasyUploadMenu.uploadMenu(conn=p.rConn(), plat=5, channel="YicheCrawl")
    for k in range(8,9):
        for i, m in p.tubes_detail(k):
            print(i['objname'])
            ep.MagicObj(i, m)
            ep.MagicTree(i)
    # testdict = "{'mode': {'code': u'carmodel_1564', 'mode': 8, 'name': u'\u6613\u8f66\u6307\u6570:\u6392\u884c\u699c:\u8d8b\u52bf:\u52c7\u58eb\u76ae\u5361'}, 'param': {'serial': [{'name': u'\u6613\u8f66\u6307\u6570:\u6392\u884c\u699c:\u8d8b\u52bf:\u52c7\u58eb\u76ae\u5361', 'value': u'carmodel_1564'}], 'timeType': 'day', 'fromTime': '2017-01-01', 'toTime': u'2018-11-14'}}"
    # testInfo = {"plat_id":333,"obj_ext":testdict, "objname":"易车指数:排行榜:趋势:指数:勇士皮卡"}
    # t = p.Tubes(testInfo)
    # print(t)