#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseSpider import iimediaBase
from middles.middlePool import ipProxy, userAgent
from items.YienItem import YienItem


import json, jsonpath
import re
from lxml import html


class Yien(iimediaBase):
    def __init__(self):
        super(Yien, self).__init__()
        ### 单日票房 、 趋势分析
        self.start_urls = [
            'http://www.cbooo.cn/BoxOffice/GetDayBoxOffice?num={}&d={}',
            'http://www.cbooo.cn/BoxOffice/getDayInfoData',
        ]

    def Request(self,url, **kwargs):
        import urllib2
        import requests
        try:
            data = kwargs['data']
        except:
            data = None
        finally:
            # del ipProxy.ipRandom['http']
            # handler = urllib2.ProxyHandler(proxies=ipProxy.ipRandom)
            # opener = urllib2.build_opener(handler)
            # urllib2.install_opener(opener)
            # req = urllib2.Request(url, data=data, headers={"User-Agent":userAgent.user_agent})
            # response = opener.open(req)
            # return response.read()
            req = requests.request(method="GET",
                                   url=url,
                                   proxies=ipProxy.ipRandom,
                                   headers = {"user-agent":userAgent.user_agent})
            return req.content


    ## 单日票房大类（单日票房，趋势分析）
    def parseSingleday(self, url):
        item = YienItem()
        contents = self.Request(url)
        contents = json.loads(contents.decode("utf8", "ignore"))
        for i in contents:
            tdate       = re.split(" |/", i['InsertDate'])[:3]
            item.time_t = "{}-{:0>2s}-{:0>2s}".format(*tdate)
            item.price  = i['Price']
            item.boxoffice = i['BoxOffice']
            item.showcount = i['ShowCount']
            item.auidencecount = i['AudienceCount']
            yield item()





