#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseSpider import iimediaBase
from middles.middleAssist import logAsisst
from middles.middleAssist import redisAsisst
from middles.middleAssist import ssdbAssist
import json, jsonpath

## define varibles name and its meaning
### delayFat 延时拥堵参数 delay factor
### wRatio 周环比 week ratio, unit %
### avgSpd 平均速度 average speed , unit km/h
### freeSpd 畅通速度 free speed , unit km/h
### cName 城市名 city name
### distName 城区名 district name
### areaCode 区域代码 area code
### delayLeg 延时车流长度 the length of traffice crowded
### pickTime 更新时间

class Amap(iimediaBase):

    def __init__(self):
        super(Amap, self).__init__()
        self.seed_url = "http://report.amap.com/ajax/getCityInfo.do?"
        self.start_urls = (
            "http://report.amap.com/ajax/districtRank.do?linksType={}&cityCode={}",
            "http://report.amap.com/ajax/getCityRank.do",
            "http://report.amap.com/ajax/cityDailyQuarterly.do?cityCode={}&year={}&quarter={}",
            "http://report.amap.com/ajax/cityMergedHourly.do?cityCode={}",
            "http://report.amap.com/ajax/congest/getHubs.do?linksType={}&prime=false&trafficid=&weekRadio=true",
            "http://report.amap.com/ajax/congest/getCongestRank.do?city={}&prime=false&trafficid="
        )
        # self.Logger = logAsisst.imLog(sys.argv[1])()
        self.seed_key = "tmp:amap:CityCode"
        print(self.count)
        self.Rconn = redisAsisst.imredis().connection()
        self.SDBconn = ssdbAssist.SSDBsession().connect()

    def getCityCode(self):
        Rconn = self.Rconn
        Sdbconn = self.SDBconn
        for i in Rconn.smembers(self.seed_key):
            yield i, Sdbconn.hget("amap:city:name", i)

    def parseCityCode(self):
        Rconn = self.Rconn
        Sdbconn = self.SDBconn
        response = self.startRequest(url=self.seed_url)
        cityCode = eval(response.content.decode("utf8"))
        for i in cityCode:
            Rconn.sadd(self.seed_key, i['code'])
            Sdbconn.hset("amap:city:name", i['code'], i["name"])
            Sdbconn.hset("amap:city:pinyin", i["code"], i['pinyin'])
        Rconn.expire(self.seed_key, 300)


    def parseDistrictRank(self, linksType):
        root_url = self.start_urls[1]
        for code, name in self.getCityCode():
            response = self.startRequest(url=root_url.format(linksType, code))
            jobj = json.loads(response.content.decode("utf8"))





if __name__ == '__main__':
    p = Amap()
    p.parseCityCode()