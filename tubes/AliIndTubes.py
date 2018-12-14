#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl  = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseTubes import BaseTubes
from spiders.AliIndSpider import AliInd

from middles.middleAssist import mysqlAssist
from middles.middleWare import EasyMethod, EasyUploadMenu
from middles.middleAssist import logAsisst
import re
import gevent
from gevent import monkey
monkey.patch_all()


logname = 'AliInd'


class AliIndTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,**kwargs):
        global logname
        super(AliIndTubes, self).__init__()
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self.obj = AliInd()
        self._Mconn = mysqlAssist.immysql()

        self.log = logAsisst.imLog(logname)()

        self.ep= EasyUploadMenu.uploadMenu(plat=7,
                                      channel="阿里指数",
                                      conn=self.Conn(),
                                      prefix="AL"
                                      )
        self.ep.setChannelCode(name="Alizs")

    def Conn(self):
        return self._Mconn

    def tubes_detail(self, code, objname):
        for tt in self.obj.parse_menu(cat= code,objname=objname):
            tt['freq'] = 2
            tt['mode'] = {"cat":tt['cat'],"mode":"A"}
            self.ep.loadSQL(tt)




def tmp_crawl(code,objname):
    sql = "select seed, seed_val from t_ext_seed_data_copy where platform='Alizs'" \
          " and pseed=%s"%code
    # p = AliIndTubes()
    # sql_result = p.Conn().query(sql)
    mconn = mysqlAssist.immysql()
    sql_result = mconn.query(sql)
    del mconn
    p= AliIndTubes()
    if sql_result:
        gs = []
        for s in sql_result:
            name = "{}:{}".format(objname,s[1])
            name = re.sub("^:", "", name)
	    p.tubes_detail(s[0], name)
	    tmp_crawl(s[0],name)	

            #gs.append(gevent.spawn(p.tubes_detail, s[0], name))
        #gevent.joinall(gs)




if __name__ == '__main__':


    tmp_crawl(code="0", objname="")
    # for k in ("70", "67", "509"):

