#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseSpider import iimediaBase
from middles.middleAssist import redisAsisst
from middles.middleAssist import logAsisst
from middles.middleAssist import ssdbAssist
from middles.middleAssist import mysqlAssist
from middles.middleWare import EasyMethod
from middles.middlePool import ipProxy, userAgent

from items.YicheItem import YicheItem

from jsonpath import jsonpath
import json
import requests
import re

# logger = logAsisst.imLog("YicheCrawl")()
headers = {"Content-Type": "application/json;charset=UTF-8"}

class Yiche(iimediaBase):

    def __init__(self):
        super(Yiche, self).__init__()
        self.seed_urls = (
            "http://index.bitauto.com/yicheindexpublic/rank/car-level",
            "http://index.bitauto.com/yicheindexpublic/data/last-date",
            "http://index.bitauto.com/ai/v4/searchparam/getCompeteCarsPublic"
        )
        self.allow_domains = ["http://index.bitauto.com/yicheindexpublic"]
        self.obj_urls = (
            "/sale/saleTrend",
            "/sale/saleCountryByMonthLine",
            "/sale/saleLevelBar",


            "/sale/saleDynamicBar",
            "/sale/saleMakeBar",
            "/sale/saleLevelBubule",
            "/sale/saleCountryPie",

            "/indextrend",
            "/praisetrend",
            "/rank/list",
        )


        self._seed_key = "tmp:yiche:CarModel"
        self._Rconn = redisAsisst.imredis().connection()
        self._SDBconn = ssdbAssist.SSDBsession().connect()
        self._Mconn = mysqlAssist.immysql()

    @staticmethod
    def lastDate(model,url=None):
        if url is None:
            rurl = "http://index.bitauto.com/yicheindexpublic/data/last-date"
        else:
            rurl = url
        parameters = {"model":model,
                      "date":"2017-12-27","timeType":"month"}
        if model == 'rank-index':
            parameters["timeType"] = "day"
        response = Yiche.startRequest(url=rurl, data=parameters)
        last_date= jsonpath(response, "$..lastDate")[0]
        return last_date

    @staticmethod
    def startRequest(url,  **kwargs):
        global headers
        print(url, kwargs['data'])
        ip = {"https": ipProxy.ipRandom["https"]}
        head = dict(headers, **{"User-Agent":userAgent.user_agent})
        response = requests.post(url=url, data = json.dumps(kwargs["data"]),
				 proxies=ip,
                                 headers=head)
        try:
            response = json.loads(response.content)
            return response
        except Exception as e:
            logger.error(e)
            return 0


    def parseMarketMonth(self, url_suffix, mod=1, **kwargs):
        """

        :param url_suffix:
        :param mod: 0,1
        :return:
        """

        if re.match(".+Trend",url_suffix):unit = "辆"
        else:unit = "%"
        freq = 4
        this = self.allow_domains[0]+url_suffix

        param1= {"timeType":"month",
                "fromTime":"2017-10-15",
                "toTime":Yiche.lastDate(model="market", url=self.seed_urls[1])}
        response = Yiche.startRequest(url=this, data=param1)
        name = jsonpath(response, "$..yAxis.name")[0]
        timeT    = jsonpath(response, "$..xAxis[*].data")[0]
        timeT    = map(EasyMethod.fuckMonthEnd,timeT)
        obj_data = jsonpath(response, "$..series[*].data")
        obj_name = jsonpath(response, "$..series[*].name")
        for objd, objn in zip(obj_data, obj_name):
            data = dict(map(None, timeT, objd))
            yield {"objname":"易车指数##市场大盘##%s##%s"%(name,objn),
                   "data":data,
                   "unit":unit,
                   "freq":freq}, {"param":param1}



    def parseMarketSeason(self, url_suffix, mod=2, **kwargs ):
        if mod < 0 or mod > 4 or not isinstance(mod, int) :
            raise ValueError("mod取值只可以是0到4的整数值")
        if mod < 2:step,freq = 3, 5
        elif mod == 2:step,freq = 1, 4
        else:step,freq = 6, 5


        this = self.allow_domains[0]+url_suffix
        objprefix = "易车指数##市场大盘##份额趋势(近%d个月均值)"%step + "##%s"
        suffix = url_suffix.split("/")[-1]
        param= {"timeType":"month"}

        for year in (2018, 2017):
            for month in range(0, 13, step):
                try:
                    tmp = "tmpyiche:" + suffix +":%s"
                    if month + step > 12:continue
                    param['fromTime'] = "%d-%02d-01" %(year, month)
                    param['toTime'] = EasyMethod.fuckMonthEnd(year=year, month=month+step)
                    response = Yiche.startRequest(url=this, data=param)
                    # type 表示 类型
                    if kwargs["type"] == 1:
                        objname = jsonpath(response, "$..series[*].data[*].name")
                        objdata = jsonpath(response, "$..series[*].data[*].symbolSize")
                        if objdata == False:
                            objdata = jsonpath(response, "$..series[*].data[*].value")

                    elif kwargs["type"] == 0:
                        objname  = jsonpath(response, "$..yAxis[*].data")[0]
                        objdata  = jsonpath(response, "$..series[*].data")[0]


                    print(objdata)
                    map(
                    lambda a,b:self._Rconn.hset(tmp % a, param['toTime'],
                                                b.decode("utf8"))
                                                if b else 1,
                        objname, objdata)



                except Exception as e:print(e)

        for k in self._Rconn.keys("tmpyiche:%s*"%suffix):
            data = self._Rconn.hgetall(k)
            objname = objprefix % k.split(":")[-1]
            yield {"objname":objname, "data":data,
                   "unit":"%", "freq":freq}, {"param":param}
            print("delete %s"%k)
            self._Rconn.delete(k)
            
            
    def SeedSaveSQL(self):
        param0 = {"id":4}
        param2 = {"subject":"serial","id":"carmodel_5426","searchName":"","from":"search"}
        response0 = Yiche.startRequest(url = self.seed_urls[0], data=param0)
        obj0 = jsonpath(response0, "$..data[*].value")[0]
        print(obj0)
        carlevels = jsonpath(response0, "$..data[*].children")[0]
        for car in carlevels:
            self._SDBconn.hset("yiche:carlevel:series",car['value'], car['name'])
            self._Mconn.insert(tbName="t_ext_seed_data_copy",
                               seed = car['value'],
                               seed_val = car['name'],platform="Yiche",
                               note = obj0, level = 1)
            # self._Mconn.insert(tbName="t_ext_plat_menu",
            #                    plat_id = 5,
            #                    name="易车指数:排行榜:%s"%car['name'],
            #                    channel_code = "yiche_crawl",
            #                    code = car['value'],
            #                    p_code = "yiche_crawl",
            #                    ext = str(car))

        response2 = Yiche.startRequest(url=self.seed_urls[2], data=param2)
        node2     = jsonpath(response2, "$..data")[0]
        for node in node2:
            carlevels = node['children']
            pseed     = node['value']
            pname     = node['name']
            print(pname, pseed)
            self._Mconn.insert(tbName="t_ext_seed_data_copy",
                               seed  = pseed,
                               seed_val = pname, platform='Yiche',
                               level=-1)
            for car in carlevels:
                value, name = car['value'], car['displayName']
                self._SDBconn.hset("yiche:carlevel:model",value, name)
                del car['isChecked'], car['saleStatus']
                self._Mconn.insert(tbName="t_ext_seed_data_copy",
                                   seed  = value,
                                   seed_val = name, platform='Yiche',
                                   pseed = pseed if pseed  else "",
                                   level = 0,
                                   note = str(car))
                # self._Mconn.insert(tbName="t_ext_plat_menu",
                #                    plat_id = 5,
                #                    name="易车指数:排行榜:%s"%name,
                #                    channel_code = pseed,
                #                    code = value,
                #                    p_code = pseed,
                #                    ext = str(car))


    def parseRank(self, code=None, name=None, **kwargs):
        for i in range(2):
            model = "口碑" if i else "指数"
            lastdate = self.lastDate(model="rank-koubei" if i else "rank-index")
            param7 = {"serial":[{"name":name,"value":code}],
                      "timeType":"month" if i else "day",
                      "fromTime":"2017-01-01",
                      "toTime":lastdate}
            tt = name.split("##")
            nam = "##".join(tt[:-1] + [model]+tt[-1:])
            url = self.allow_domains[0]  + self.obj_urls[7+i]
            response = Yiche.startRequest(url=url, data= param7)

            objtime  = jsonpath(response, "$..xAxis[*].data")[0]
            objtime  = map(EasyMethod.fuckMonthEnd, objtime) if i else objtime
            objdata  = jsonpath(response, "$..series[*].data")[0]
            yield {"objname":nam, "data":dict(zip(objtime, objdata)),
                   "unit":"", "freq":4}, {"param":param7}

    def parseSales(self, code, name, **kwargs):
        if kwargs['pid'] > 6 :yield 0
        param9 = {"id":kwargs["pid"], "value":code}

        url    = self.allow_domains[0] + self.obj_urls[9]
        response = Yiche.startRequest(url, data = param9)
        objdetail= jsonpath(response, "$..thead[*].name")[0]
        objtime  = objdetail[0]
        objname  = objdetail[2]
        objtime  = EasyMethod.fuckMonthEnd(re.sub("[^0-9]","",objtime))
        objdata  = jsonpath(response, "$..tbody")[0]
        for obj in objdata:
            yield {"objname":"%s##%s##%s"%(name, objname, obj['name']),
                   "data":{objtime:obj['index']},
                   "unit":"辆","freq":4}, {"param":param9}

        self.parseSales(code=code, name=name, pid=kwargs['pid']+1)

if __name__ == '__main__':
    p = Yiche()
    p.SeedSaveSQL()
    # for i in p.parseMarketMonth(url_suffix=p.obj_urls[2], mod=1):
    #     print(i["objname"])
    #     print(i["data"])
    # p.parseMarketSeason(url_suffix=p.obj_urls[-1], mod=2, type=1)
    # for i in p.parseMarketSeason(url_suffix=p.obj_urls[-1], mod=2, type=1):
    #     print(i['objname'])
    #     print(i)
    # t = p.parseSales(type='rank-koubei',code='brand',name='xxx')
    # for i in t:
    #     print(i)
