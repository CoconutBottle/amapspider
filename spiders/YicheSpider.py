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


    def parseMarketData(self, url_suffix, freq=1):
        """

        :param url_suffix:URL后缀
        :param freq: 更新频率 4/5 month/season
        :return:
        """
        this = self.allow_domains[0]+url_suffix
        param= {"timeType":"month",
                "fromTime":"2017-10-15",
                "toTime":Yiche.lastDate(model="market", url=self.seed_urls[1])}
        response = Yiche.startRequest(url=this, data=param)
        obj_name = jsonpath(response, "$..yAxis.name")[0]
        timeT    = jsonpath(response, "$..xAxis[*].data")[0]
        timeT    = map(EasyMethod.fuckMonthEnd,timeT)
        obj_data = jsonpath(response, "$..series[*].data")[0]

        data     = dict(map(None, timeT, obj_data))
        print(data)


    def parseCarModel(self):
        global headers
        parameters = {"id":4}
        response = requests.post(url=self.seed_urls[0], data=json.dumps(parameters),
                                 headers=headers)
        response = json.loads(response.content)
        children = jsonpath(response, "$..children")[0]
        for i in children:
            self._Rconn.sadd(self._seed_key, i['value'])
            self._SDBconn.hset('yiche:car:name', i['value'], i['name'])
        self._Rconn.expire(self._seed_key, 300)


    def getCarModel(self):
        for i in self._Rconn.smembers(self._seed_key):
            yield i, self._SDBconn.hget('yiche:car:name', i)


    def parseCarSerial(self):
        global headers
        parameters = {"subject":"serial","id":"carmodel_5422","searchName":"","from":"search"}
        root_url = self.seed_urls[2]
        response = requests.post(url=root_url, data=json.dumps(parameters),
                                 headers=headers)
        print(response.content)

    def parseRank(self, value, name):
        global headers
        root_url = self.start_urls[0]
        for chId in (4, 5, 6):
            try:
                parameters = {"id": chId, "value":value}
                response   = requests.post(url=root_url, data=json.dumps(parameters),
                                           headers=headers)
                response = json.loads(response.content)
            except Exception as e:
                print(e)
                return -1
            else:
                response = jsonpath(response, "")





if __name__ == '__main__':
    p = Yiche()

    p.parseMarketData(url_suffix=p.obj_urls[0])