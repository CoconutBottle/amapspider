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
from middles.middleAssist import redisAsisst
from middles.middleWare import  EasyMethod

from BaseTubes import  BaseTubes
import time
import threading, multiprocessing
plock = multiprocessing.Lock()
tlock = threading.Lock()


class RoboTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,**kwargs):
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self.obj = Robo(hkey=kwargs["hkey"])
        self.sql = mysqlAssist.immysql()
        self.channelCode = None
        self.redis = redisAsisst.imredis().connection()
        self.Logger = logAsisst.imLog(sys.argv[1])()
        self.feature_code = "seen:code"

    def tubes_allchannel(self):
        for i in self.obj.parseChannelItem():
            if "RRP1" == i["code"]:
                self.channelCode = i["code"]
                self.sql.insert(tbName="t_ext_data_channel",
                                channel_name = i["source"],
                                plat_id = self.plat_id,
                                channel_code = i["code"])
                # self.sql.execute(t)
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
                # self.sql.execute(t)
                self.tubes_menus(i["code"])
            else:
                self.sql.insert(tbName="t_ext_plat_menu",
                                plat_id=2,
                                channel_code=self.channelCode,
                                name=i["source"],
                                code=i["code"],
                                p_code=code,
                                ext=i["ext"])
                # self.sql.execute(t)

    def tubes_detail(self, code, **kwargs):

        try:
            self.pick_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            dataflow = self.obj.parse(code=code, retries=0)
            data = map(None, dataflow["data"].keys(), dataflow["data"].values())
            plock.acquire()
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
                            pick_time=self.pick_time)

            p=self.sql.query("select id from t_ext_data_obj "
                             "where code = '%s' and plat_id=2" % kwargs["pcode"])
            tt = "insert ignore into t_ext_data_node(obj_id, time_t, amo) " \
                 "values ( '%s'" % p[0][0]
            print(tt)
            self.Logger.info(tt)


            tt = tt + ",%s, %s)"
            self.sql.executemany(tt, tuple(data))
            # for t in tuple(data):
            #     self.sql.execute(tt % t)
            self.redis.sadd(self.feature_code, code)
            tlock.release()
            plock.release()
        except Exception as e:
            self.Logger.error(e)
            tlock.release()
            plock.release()
        else:
            return dataflow["data"]

    def tubes_heartbeat(self, offset,feature= None):
        print("entering heart beat function")
        if feature is None:
            tm = "select code, ext from t_ext_plat_menu\
                                    where ext <> '' group by code, ext order by id\
                                     limit %d, 1000" % (offset)
        else:
            tm = "select code, ext from t_ext_plat_menu\
                                where ext <> '' and channel_code='%s' group by code, \
                                 ext order by id\
                                 limit %d, 1000" % ( feature,offset )
        tmp = self.sql.query(tm)
        for i in tmp:
            yield i

    def tmp_crawl(self, feature = None):

        count = feature["offset"]*10000
        MAX_COUNT = count + 10000
        retry = 0
        feature = feature["feature"]
        if feature != '771263':
            self.feature_code = "seen:code:{}".format(feature)
        while True:
            if count >= MAX_COUNT:
                break
            tmp = self.tubes_heartbeat(count, feature)
            if not tmp:
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
                    if self.redis.sismember(name=self.feature_code, value=code):
                        continue
                    self.tubes_detail(code=code, pcode=pcode)
                except Exception as e:
                    self.Logger.error(e)
                else:

                    self.Logger.info(["enter",feature,pcode, code])
                    time.sleep(0.08)
            count += 1000


    def Tubes(self, taskinfo):
        import datetime

        try:
            self.plat_id = taskinfo["plat_id"]
            code = eval(taskinfo["obj_ext"])["indicId"]
            dataflow = self.obj.parse(code=code, retries=0)
            taskinfo['report_time'] = '%s' % \
                                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            taskinfo["data"] = dataflow["data"]
            taskinfo['process_code'] = os.getpid()

        except Exception as e:
            self.Logger.error(["TubesError[%d]" % os.getpid(), e])

        else:
            return taskinfo

    def __del__(self):
        self.Logger.info("-----END-----")
        del self.sql

def gmain(feature, func):
    gs = [gevent.spawn(func,
            {"feature": feature["feature"],
             "offset": feature['offset']+i*1000})
          for i in range(10)]
    gevent.joinall(gs)

def main(feature, count, hkey):
    print("test....")

    p = RoboTubes(platid=2, hkey=hkey)
    # for i in range(count):
    # 	p.tmp_crawl({"feature":feature,"offset":i*10000})

    ts = [threading.Thread(name=i,target=gmain,
                           args=({"feature":feature,"offset":i},p.tmp_crawl,))
          for i in range(count)]
    for t in ts:
        print(t)
        t.start()
        time.sleep(2)


    for t in ts:
        t.join()

if __name__ == '__main__':
    import gevent
    from gevent import monkey
    monkey.patch_all()
    redisAsisst.initAccount()
    username = ("zzm", "cwf", "wjh", "llb", "fwb","com")
    for i in username:
        EasyMethod.RoboEasyLogin(i)

    tmp = {'1138921':8,'402273':17,'771263':51,
           '632815':23,'RRP1':128,'RRP1349982':13}
    # gs = [threading.Thread(target=main, args=(i, tmp[i], u, ))
    #       for i,u in zip(tmp,username)]
    gs = [multiprocessing.Process(target=main, args=(i, tmp[i], u,))
          for i, u in zip(tmp, username)]

    for t in gs:
        print(t)
        t.start()
    #     time.sleep(5)
    # for t in gs:
    #     t.join()
