# -*- coding:UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os
curUrl = os.path.dirname(__file__)
parUrl = os.path.abspath(os.path.join(curUrl, os.pardir))
sys.path.append(parUrl)

from BaseTubes import BaseTubes
from spiders.zhongtouSpider import ZhongTou
from spiders import zhongtouSpider
from middles.middleAssist import mysqlAssist
from middles.middleWare import EasyDecorate
from middles.middleAssist import redisAsisst
logname = "test"


class zhongtouTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,**kwargs):
        global logname
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self._Rconn = redisAsisst.imredis().connection()
        self._Mconn = mysqlAssist.immysql()

    def rConn(self, mode = 'm'):
        if mode == 'm':
            return self._Mconn
        elif mode == 'r':
            return self._Rconn

    # @EasyDecorate.tryexcept(logname)
    def tubes_detail(self, code):
        import re

        obj = ZhongTou()
        obj.auto_crawl()
        for i in self._Rconn.smembers("ZT:obj"):
            yield eval(i)


    def Tubes(self, taskinfo):
        import datetime
        obj = ZhongTou()

        self.plat_id = taskinfo["plat_id"]
        code = eval(taskinfo["obj_ext"])
        mode = code['mode']



        obj.channelname = (mode['name'], mode['code'])

        dataflow = next(obj.parse_detail(url=mode['url'],
                                    specify=1,
                                    objname = taskinfo['obj_name']))
        taskinfo['report_time'] = '%s' % \
                                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        taskinfo["data"] = dataflow["data"]
        taskinfo['process_code'] = os.getpid()
        return  taskinfo



if __name__ == '__main__':
    from middles.middleWare import EasyUploadMenu
    choice = raw_input("是否决定初始化数据指标(y/n)? 这可能造成数据紊乱:".decode("utf8"))
    if choice != 'y':
        raise ValueError("初始化退出")
    p = zhongtouTubes()
    zhongtouSpider.giveCookie('set')
    # test = {"obj_id":"xxxx","obj_name":"中国投资:沪深股市:上证综合指数月末收盘",
    #         "obj_ext":"{'mode': {'url': u'http://www.macrodb.com:8000/dat
    # a_m/prg/showdata.asp?ffrm=1&prg=tab&rnd1=.5070462', 'code': 'TRP1',
    # 'mode': 'Z', 'name': u'\u6caa\u6df1\u80a1\u5e02'}}",
    # 'mode': 'Z', 'name': u'\u6caa\u6df1\u80a1\u5e02'}}",
    #         "plat_id":"6"}
    ep = EasyUploadMenu.uploadMenu(conn=p.rConn(), plat=6,
                                   channel="中国投资协会", prefix="ZT")
    ep.setChannelCode("chinainvest")
    p.rConn('r').delete('ZT:obj')
    for i in p.tubes_detail('test'):
        mode = {}
        mode["mode"] = i["mode"]


        del i["mode"]
        ep.MagicObj(i, mode)
        ep.MagicTree(i)

    # tt = p.Tubes(test)
    # print(tt['obj_name'])
    # print(tt)

