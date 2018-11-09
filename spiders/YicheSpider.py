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

from jsonpath import jsonpath
import json
import requests

# logger = logAsisst.imLog(sys.argv[1])()
headers = {"Content-Type": "application/json;charset=UTF-8"}

class Yiche(iimediaBase):

    def __init__(self):
        super(Yiche, self).__init__()
        self.seed_urls = (
            "http://index.bitauto.com/yicheindexpublic/rank/car-level",
            "http://index.bitauto.com/yicheindexpublic/data/last-date",
            "http://index.bitauto.com/ai/v4/searchparam/getCompeteCarsPublic"
        )

        self.start_urls = (
            "http://index.bitauto.com/yicheindexpublic/rank/list",
            "http://index.bitauto.com/yicheindexpublic/sale/saleTrend",
            "http://index.bitauto.com/yicheindexpublic/sale/saleLevelBar",
            "http://index.bitauto.com/yicheindexpublic/sale/saleCountryByMonthLine",
        )

        self._seed_date = Yiche.lastDate(url=self.seed_urls[1])
        self._seed_key = "tmp:yiche:CarModel"
        self._Rconn = redisAsisst.imredis().connection()
        self._SDBconn = ssdbAssist.SSDBsession().connect()

    @staticmethod
    def lastDate(url):
        global headers
        parameters = {"model":"market","date":"2017-12-27","timeType":"month"}
        response = requests.post(url=url, data = json.dumps(parameters),
                                 headers=headers)
        response = json.loads(response.content)
        last_date= jsonpath(response, "$..lastDate")[0]
        return last_date

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

    p.parseCarSerial()