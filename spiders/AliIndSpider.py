# -*- coding:UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os
curUrl = os.path.dirname(__file__)
parUrl = os.path.abspath(os.path.join(curUrl, os.pardir))
sys.path.append(parUrl)

from BaseSpider import iimediaBase
from middles.middlePool import ipProxy, userAgent
from items.CommonItem import commonItem
from lxml import html
from middles.middleWare import digitalConfig
from middles.middleAssist import mysqlAssist
import re
import jsonpath, json
from itertools import chain
layer = 1
indt_dict = {
    "purchaseIndex1688":"1688采购指数",
    "supplyIndex":"1688供应指数",
    "purchaseIndexTb":"淘宝采购指数",
    1:"同比上周增幅",
    0:"指数"
}

class xpathRules(object):
    prefix   = "//div[@id=\"aliindex-masthead\"]/div/div[3]/div"

    xkey     = "//*[@id=\"aliindex-masthead\"]/div/div[3]/div[{}]/div/ul/li/a/@data-key"
    xhkey    = "//*[@id=\"aliindex-masthead\"]/div/div[3]/div[{}]/@data-key"

    xname    = "//*[@id=\"aliindex-masthead\"]/div/div[3]/div[{}]/div/ul/li/a/@title"
    xhname   = "//*[@id=\"aliindex-masthead\"]/div/div[3]/div[{}]/p/a/text()"




class AliInd(iimediaBase):
    def __init__(self, open_sql = False):
        super(AliInd, self).__init__()
        self.start_urls = 'https://index.1688.com/alizs/market.htm?spm=a262ha.8884008.0.0.uCrTZL'
        self.seed_url   = 'https://index.1688.com/alizs/market.htm?userType=purchaser&cat='
        del ipProxy.ipRandom['https']
        self.proxies = ipProxy.ipRandom
        self.headers = {"user-agent":userAgent.user_agent}
        self.tmpurl = ""
        if open_sql:
            self._Mconn = mysqlAssist.immysql()

    def Request(self, url, callback, **kwargs):
        import urllib2
        handler = urllib2.ProxyHandler(self.proxies)
        opener  = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        try:
            import urllib
            data = urllib.urlencode(kwargs['data']).encode("utf8")
        except:
            req  = urllib2.Request(url, headers=self.headers)
        else:
            req  = urllib2.Request(url,data=data, headers=self.headers)

        contents= urllib2.urlopen(req).read()
        if callback is None:
            return contents.decode("utf8")
        else:
            callback(contents.decode("utf8"))

    def parse_url(self, response, **kwargs):
        """

        :param response:获取爬取url特征码
        :return:
        """


        tree = html.fromstring(response)
        data_key = tree.xpath(xpathRules.xkey.format(kwargs['layer']))
        data_key = chain(data_key, tree.xpath(xpathRules.xhkey.format(kwargs['layer'])))

        data_title = tree.xpath(xpathRules.xname.format(kwargs['layer']))
        data_title = chain(data_title, tree.xpath(xpathRules.xhname.format(kwargs['layer'])))



        for i, k in zip(data_key,data_title):
            dkey = i
            dtitle = re.sub("、".decode("utf8"), "/",k)
            try:
                pkey = kwargs['pkey']
            except:pkey = 0
            self._Mconn.insert(tbName="t_ext_seed_data",
                               seed=dkey,
                               pseed=pkey,
                               seed_val=dtitle,
                               platform="Alizs",
                               level=0)

            print(dkey)
            print(dtitle)
            response = self.Request(url=self.seed_url+dkey, callback=None)
            self.parse_url(response= response, layer=kwargs["layer"]+1, pkey = dkey)


    def parse_parkey(self, response):
        """

        :param response: get parent key
        :return: Request
        """
        tree = html.fromstring(response)

        Key = tree.xpath("{}|{}".format(xpathRules.xheadPKey, xpathRules.xparKey))

        for cat in Key[:2]:
            self.tmpurl = self.seed_url+cat
            self.Request(url=self.tmpurl,
                         callback=self.parse)


    def parse(self, response):
        """

        :param response:
        :return: obj指标相关数据
        """
        from itertools import chain

        global indt_dict

        item = commonItem()

        tree = html.fromstring(response)
        objname = tree.xpath("{}|{}".format(xpathRules.xheadPname,
                                            xpathRules.xheadSname))
        data = tree.xpath(xpathRules.xdata)
        data_json = json.loads(data[0])

        last_dates= tree.xpath(xpathRules.xlastDate)[0]

        for pkey in data_json:

            data_sets = jsonpath.jsonpath(data_json[pkey], "$..history")
            for i, data_obj in enumerate(data_sets):
                obj = chain([indt_dict[pkey]] , objname , [indt_dict[i]])

                item.objname = ":".join(obj)
                item.mode    = {"url":re.search("cat=(.+)$",self.tmpurl).group(1),
                                "key":pkey, "mode":"Ah"}

                date     = digitalConfig.getdatelist(start=last_dates,
                                                     between=len(data_obj),
                                                     reverse=True)
                item.data= dict(zip(date, data_obj))
                # print item.objname, item()
        sKey = tree.xpath("{}|{}".format(xpathRules.xheadSKey, xpathRules.xsonKey))
        tmp = self.tmpurl
        for i in sKey:
            if i == "-1":continue
            self.tmpurl = self.tmpurl+","+i
            print(self.tmpurl)
            self.tmpurl = tmp




def f():
    for i in range(4):
        yield i
        for k in range(5,8):
            yield k
            yield i




if __name__ == '__main__':
    p = AliInd(open_sql=True)

    res = p.Request(p.start_urls, None)
    p.parse_url(response=res, layer=1)
