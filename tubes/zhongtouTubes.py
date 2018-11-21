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

logname = "test"


class zhongtouTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,**kwargs):
        global logname
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)

        self._Mconn = mysqlAssist.immysql()

    def rConn(self):
        return self._Mconn

    # @EasyDecorate.tryexcept(logname)
    def tubes_detail(self, code):
        import re
        obj = ZhongTou()
        for k, i in enumerate(obj.auto_crawl()):

            obj_code = re.search("rnd1=.*\.(\d+)",i).group(1)
            print(obj_code)
            for item in obj.parse_detail(url=i, channelname=obj.channelname[k]):
                yield item

    def Tubes(self, taskinfo):
        import datetime
        obj = ZhongTou()
        self.plat_id = taskinfo["plat_id"]
        code = eval(taskinfo["obj_ext"])
        mode = code['mode']

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
    # zhongtouSpider.giveCookie('set')
    # test = {"obj_id":"xxxx","obj_name":"中国投资频道:国内生产总值:上交所日均成交额",
    #         "obj_ext":"{'mode': {'url': u'http://www.macrodb.com:8000/data_m/prg/showdata.asp?ffrm=1&prg=tab&rnd1=.7232259', 'mode': 1, 'name': u'\u4e2d\u56fd\u6295\u8d44\u9891\u9053:\u4f01\u4e1a\u6548\u76ca:\u672c\u6708\u6df1\u8bc1\u7efc\u5408\u6307\u6570\u6700\u4f4e\u70b9'}}",
    #         "plat_id":"6"}
    ep = EasyUploadMenu.uploadMenu(conn=p.rConn(), plat=6,
                                   channel="中国投资协会", prefix="ZT")
    ep.setChannelCode("chinainvest")
    for i in p.tubes_detail('test'):
        mode = {}
        mode["mode"] = i["mode"]

        del i["mode"]
        ep.MagicObj(i, mode)
        ep.MagicTree(i)
    # print(p.Tubes(test))


