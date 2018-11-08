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

    def parseCityCode(self):
        Rconn = redisAsisst.imredis().connection()
        Sdbconn = ssdbAssist.SSDBsession().connect()
        response = self.startRequest(url=self.seed_url)
        cityCode = eval(response.content.decode("utf8"))
        for i in cityCode:
            Rconn.sadd(self.seed_key, i['code'])
            Sdbconn.hset("amap:city:name", i['code'], i["name"])
            Sdbconn.hset("amap:city:pinyin", i["code"], i['pinyin'])
        Rconn.expire(self.seed_key, 500)
        print("over")

if __name__ == '__main__':
    p = Amap()
    p.parseCityCode()