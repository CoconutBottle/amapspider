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

from items.YicheItem import YicheItem

from jsonpath import jsonpath
import json
import requests

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
        )


        self._seed_key = "tmp:yiche:CarModel"
        self._Rconn = redisAsisst.imredis().connection()
        self._SDBconn = ssdbAssist.SSDBsession().connect()

    @staticmethod
    def lastDate(model, url):
        parameters = {"model":model,
                      "date":"2017-12-27","timeType":"month"}
        if model == 'rank-index':
            parameters["timeType"] = "day"
        response = Yiche.startRequest(url=url, data=parameters)
        last_date= jsonpath(response, "$..lastDate")[0]
        return last_date

    @staticmethod
    def startRequest(url,  **kwargs):
        global headers
        response = requests.post(url=url, data = json.dumps(kwargs["data"]),
                                 headers=headers)
        try:
            response = json.loads(response.content)
            return response
        except Exception as e:
            logger.error(e)
            return 0


    def parseMarketMonth(self, url_suffix, mod=1):
        """

        :param url_suffix:
        :param mod: 0,1
        :return:
        """
        if mod !=1 and mod !=0 and mod !=2:
            raise ValueError("mod取值只可以是1或0或2")

        this = self.allow_domains[0]+url_suffix

        param= {"timeType":"month",
                "fromTime":"2017-10-15",
                "toTime":Yiche.lastDate(model="market", url=self.seed_urls[mod])}
        response = Yiche.startRequest(url=this, data=param)
        name = jsonpath(response, "$..yAxis.name")[0]
        timeT    = jsonpath(response, "$..xAxis[*].data")[0]
        timeT    = map(EasyMethod.fuckMonthEnd,timeT)
        obj_data = jsonpath(response, "$..series[*].data")
        obj_name = jsonpath(response, "$..series[*].name")
        for objd, objn in zip(obj_data, obj_name):
            data = dict(map(None, timeT, objd))
            yield {"objname":"易车指数:市场大盘:%s:%s"%(name,objn), "data":data}



    def parseMarketSeason(self, url_suffix, mod=1, **kwargs ):
        if mod < 0 or mod > 3 or not isinstance(mod, int) :
            raise ValueError("mod取值只可以是0到4的整数值")
        if mod < 2:step = 3
        elif mod == 2:step = 1
        else:step = 6


        this = self.allow_domains[0]+url_suffix
        objprefix = "易车指数:市场大盘:份额趋势(近%d个月均值)"%step + ":%s"
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

                    self._Rconn.expire(tmp, 300)

                except Exception as e:print(e)

        for k in self._Rconn.keys("tmpyiche:%s*"%suffix):
            data = self._Rconn.hgetall(k)
            objname = objprefix % k.split(":")[-1]
            yield {"objname":objname, "data":data}
            print("delete %s"%k)
            self._Rconn.delete(k)

if __name__ == '__main__':
    p = Yiche()

    # for i in p.parseMarketMonth(url_suffix=p.obj_urls[2], mod=1):
    #     print(i["objname"])
    #     print(i["data"])
    # p.parseMarketSeason(url_suffix=p.obj_urls[-1], mod=2, type=1)
    for i in p.parseMarketSeason(url_suffix=p.obj_urls[-1], mod=2, type=1):
        print(i['objname'])
        print(i)