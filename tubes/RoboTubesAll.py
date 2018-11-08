#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
from spiders.RoboSpider import Robo
from middles.middleAssist import mysqlAssist, logAsisst
from items.iMqIMData import iMqIMDataCollectItem
from BaseTubes import  BaseTubes
import time
import threading
tlock = threading.Lock()


class RoboTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None):
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self.obj = Robo()
        self.sql = mysqlAssist.immysql()
        self.channelCode = None
        self.redis = ""
        self.Logger = logAsisst.imLog("RoboCrawls")()
        self.pick_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def tubes_allchannel(self):
        for i in self.obj.parseChannelItem():
            if "RRP1" == i["code"]:
                self.channelCode = i["code"]
                self.sql.insert(tbName="t_ext_data_channel",
                                channel_name = i["source"],
                                plat_id = self.plat_id,
                                channel_code = i["code"])
		try:
                    self.tubes_menus(i["code"])
		except:pass

    def tubes_menus(self, code):
        for i in self.obj.parseItem(code):
            if i["value"]:
                self.sql.insert(tbName="t_ext_plat_menu",
                                plat_id = self.plat_id,
                                channel_code = self.channelCode,
                                name = i["source"],
                                code = i["code"],
                                p_code = None if code == self.channelCode else code)
                self.tubes_menus(i["code"])
            else:
                self.sql.insert(tbName="t_ext_plat_menu",
                                plat_id=2,
                                channel_code=self.channelCode,
                                name=i["source"],
                                code=i["code"],
                                p_code=code,
                                ext=i["ext"])

    def tubes_detail(self, code, **kwargs):

        try:
            dataflow = self.obj.parse(code=code, retries=0)
            #tt = "insert ignore into t_ext_data_node(obj_id, time_t, amo) values ( "%s"
            #self.Logger.info(tt)
            #tt = tt + ",%s, %s)"
            #print(tt)
            data = map(None, dataflow["data"].keys(), dataflow["data"].values())
            tlock.acquire()
	    dd = dict(dataflow["ext"], **{'indicId:':code})
            self.sql.insert(tbName="t_ext_data_obj",
                            plat_id = self.plat_id,
                            name = dataflow["ext"]["name"],
                            code = kwargs["pcode"],
                            frequence_mode = dataflow["frequency"],
                            frequence = dataflow["value"],
                            unit = dataflow["unit"],
                            data_source = dataflow["source"],
                            note = dataflow["pcode"],
                            update_time = dataflow["update_time"],
                            start_time  = dataflow["start_time"],
                            end_time    = dataflow["end_time"],
                            is_end = dataflow["is_end"],
                            ext = str(dd),
                            pick_time = self.pick_time)
	    p = self.sql.query("select id from t_ext_data_obj where code = '%s' and plat_id=2"%kwargs["pcode"])
	    tt = "insert ignore into t_ext_data_node(obj_id, time_t, amo) values ( '%s'" % p[0][0]
            print(tt)
	    #self.Logger.info(tt)
            tt = tt + ",%s, %s)"


            self.sql.executemany(tt, tuple(data))
            tlock.release()
        except Exception as e:
            self.Logger.error(e)
        else:
            return dataflow["data"]

    def tubes_heartbeat(self, offset,feature= None):
        print("entering heart beat function")
        if feature is None:
            tmp = self.sql.query("select code, ext from t_ext_plat_menu\
                                    where ext <> '' group by code, ext order by id\
                                     limit %d, 1000" % (offset*1000))
        else:
            tmp = self.sql.query("select code, ext from t_ext_plat_menu\
                                where ext <> '' and channel_code='%s' group by code, ext order by id\
                                 limit %d, 1000" % ( feature,offset * 1000))

        for i in tmp:
            yield i

    def tmp_crawl(self, feature = None):
        count = feature["offset"]*10000
        MAX_COUNT = count + 10000
        retry = 0
        feature = feature["feature"]
        while True:
            if count >= MAX_COUNT:
                break
            tmp = self.tubes_heartbeat(count, feature)
            if tmp is None:
                retry += 1
                if retry > 50:
                    break
                self.Logger.info("Waiting Sleep 500 sec")
                time.sleep(500)
                continue
            retry = 0
            for i in tmp :
                print(i)
                try:
                    pcode = i[0]
                    code  = eval(i[1])["indicId"]
                    self.tubes_detail(code=code, pcode=pcode)
                except Exception as e:
                    self.Logger.error(e)
                else:
                    self.Logger.info(["enter",pcode, code])
                    time.sleep(0.08)
            count += 1

    def Tubes(self, **kwargs):
        try:
            self.plat_id = kwargs["plat_id"]
            pcode= kwargs["obj_code"]
            code = eval(kwargs["ext"])["indicId"]
            dataflow = self.obj.parse(code=code, retries=0)
            # self.sql.insert(tbName="t_ext_data_obj",
            #                 plat_id=self.plat_id,
            #                 code=pcode,
            #                 update_time=dataflow["update_time"],
            #                 end_time=dataflow["end_time"],
            #                 is_end=dataflow["is_end"])
        except Exception as e:
            self.Logger.error(e)
            return {"stat":2,"note":e}
        else:
            return {"data":dataflow["data"],"stat":1}

    def __del__(self):
        self.Logger.info("-----END-----")
        del self.sql



def f(t):
    import requests
    for i in range(3):
        print(requests.get(t), t, i)
        time.sleep(1)

def main(feature, count):
    import gevent
    from gevent import monkey
    monkey.patch_all()
    #p= RoboTubes(platid=2)
    print("test....")
    #asy = [ gevent.spawn(p.tmp_crawl, {"feature":"632815","offset":i*10000}) for i in range(23)]
    #gevent.joinall(asy)
    for i in range(count):
    	p.tmp_crawl({"feature":feature,"offset":i*10000})
    #p.tubes_allchannel()

import gevent
from gevent import monkey
monkey.patch_all()
p = RoboTubes(platid=2)

tmp = {'1138921':8,'402273':17,'771263':51,'RRP1':128,'RRP1349982':13}
for i in tmp:
    main(i,tmp[i])

#gs = [gevent.spawn(main, i, tmp[i]) for i in tmp]
#gevent.joinall(gs)
