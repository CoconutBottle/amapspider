#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
from BaseSpider import iimediaBase
from items.RoboItem import CommonItem, RoboItem
from middles.middleWare import EasyMethod as Ey
from middles.middleAssist import logAsisst
import jsonpath, requests
import json, time, random, re
from middles.middlePool import userAgent


user_data = {
    "username": "18100226031",
    "password": "z20180517!",
    "rememberMe": "false",
    "app": "cloud"
}

class Robo(iimediaBase):
    def __init__(self,hkey="Robo"):

        name = "RoboSpider"
        self.start_urls = 'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/level/0'
        self.urlContainer = [
            'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/%s',
            'https://gw.datayes.com/rrp_adventure/web/dataCenter/indic/%s?compare=false'
        ]
        self.key = hkey
        self.cookie =Ey.getCookie(self.key)
        self.Logger = logAsisst.imLog(sys.argv[1])()


##  First Channel
    def parseChannelItem(self, retries = 0, code=None):
        """

        :param retries: must be 0
        :param code: must be None
        :return: item object
        """
        responset = self.retry(url=self.start_urls, retries=retries,
                               func= self.parseChannelItem)
        data = jsonpath.jsonpath(responset, "$..data")[0]
        items = CommonItem()
        for item in data:
            items.code = item["id"]
            items.source = item["nameCn"]
            items.value = item["hasChildren"]
            yield items()



## Second Channel
## crawl its childrendata's code and name
    def parseItem(self, code, retries = 0):
        """

        :param code: 频道代码
        :param retries: 0
        :return: item object
        """
        print(code)
        responset = self.retry(url=self.urlContainer[0] % code,
                               retries=retries, code=code,func=self.parseItem)
        items = CommonItem()
        try:
            tmpObj   = jsonpath.jsonpath(responset, "$..data.childData")[0]
            for item in tmpObj:

                    items.source = item["nameCn"]
                    items.value  = item["hasChildren"]
                    items.code   = item["id"]
                    print(items.source)
                    if items.value == False:
                        items.ext = str({"indicId":item["indicId"]})
                    print(items())
                    yield items()
        except Exception as e:
            print(e)


    def parse(self, code, **kwargs):
        """

        :param code: 节点代码
        :param kwargs: retries = 0  retries must be equal zero
        :return: item object
        """
        response = self.retry(url= self.urlContainer[1] % code,  retries=kwargs["retries"],
                              code = code, func=self.parse)
        items = RoboItem()
        try:
            dateValue = jsonpath.jsonpath(response, "$..periodDate")
            dateValue = map(Ey.fuckAntiNum, dateValue)
            #print(jsonpath.jsonpath(response, "$..dataValue"))
            items.data = dict(zip(dateValue,
                                  jsonpath.jsonpath(response, "$..dataValue")))
        except Exception as e:
            print(e)
            items.data = {}
        source_msg = jsonpath.jsonpath(response, "$..indic")[0]
        del response
        items.update_time = source_msg["updateTime"]
        items.unit        = source_msg["unit"]
        items.is_end      = 1 if source_msg["isUpdate"] == False else 0

        items.start_time  = source_msg["beginDate"]
        items.end_time    = source_msg["periodDate"]
        items.source      = source_msg["dataSource"]
        items.frequency   = Ey.frequency2id(source_msg["frequency"])
        items.value       = source_msg["frequency"] if items.frequency == 100 else ""
        items.ext         = {"region":source_msg["region"],
                             "country":source_msg["country"],
                             "name":source_msg["indicName"]}
        ## 'pcode' var xiangdangyu  'note' field
        items.pcode       = source_msg["statType"]
        #print(items())
        return  items()




    def retry(self, url, retries, func, code=None):
        responset = self.startRequest(url=url, retries=retries)
        responset = responset.content.decode("utf8", "ignore")
        responset = json.loads(responset)
        webcode = jsonpath.jsonpath(responset, "$..code")[0]
        self.Logger.info([url, "msg %d"%webcode])
        if webcode < 0 and retries < 3:
            if webcode == -403:
                print(webcode ,"Need login. Wait 5 sec")
                time.sleep(5)
                Ey.RoboEasyLogin(self.key)
                print("Retry Login...%d " % retries)
                time.sleep(5)
                self.cookie = Ey.getCookie(self.key)
                func(retries=retries + 1, code=code)
            else:
                p = random.randint(5, 15)
                self.Logger.error(("ErrorCode %d :Sleep %d sec ..." % (webcode, p)))
                time.sleep(p)
                func(retries=retries + 1, code=code)
        if retries == 3 and webcode < 0:
            raise ValueError("HTTPERROR OVER MAX RETRY TIME")
        print("SuccessCode %d " % webcode)
        return responset


if __name__ == '__main__':
    p = Robo()
    for i in p.parseChannelItem():
        print(i)
