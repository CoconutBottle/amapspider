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
from middles.middleWare import EasyDecorate
import re
import jsonpath, json
from itertools import chain
import gevent
from gevent import monkey
monkey.patch_all()

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

    xdata  = "//input[@id=\"main-chart-val\"]/@value"
    xlastday = "//*[@id=\"main-chart-lastDate\"]/@value"



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

    @EasyDecorate.try_except_callself
    def Request(self, url, callback, **kwargs):

        import requests

        try:
            # import urllib
            data = kwargs['data']
            # data = urllib.urlencode(kwargs['data']).encode("utf8")
        except:
            contents = requests.get(url=url, headers=self.headers
                                    , proxies=self.proxies)
            # req  = urllib2.Request(url, headers=self.headers)
        else:
            contents = requests.post(url=url, headers=self.headers,data=data,
                                     proxies=self.proxies)
            # req  = urllib2.Request(url,data=data, headers=self.headers)

        contents= contents.content
        if callback is None:
            return contents.decode("utf8")
        else:
            callback(contents.decode("utf8"))

    def g_event(self,dkey,layer):
        response = self.Request(url=self.seed_url+dkey,
                                callback=None)
        self.parse_url(response= response,
                       layer=layer+1,
                       pkey = dkey)

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

        gs = [gevent.spawn(self.g_event, p, layer) for p in data_key]
        gevent.joinall(gs)




    def parse_menu(self, cat="", objname=""):
        url = self.seed_url+cat
        response = self.Request(url = url,callback=None)
        response = html.fromstring(response)

        data_sets= response.xpath(xpathRules.xdata)
        data_sets= json.loads(data_sets[0])

        last_day = response.xpath(xpathRules.xlastday)[0]
        timeT    = digitalConfig.getdatelist(last_day, )

        for k in data_sets:
            # obj = "{}:{}".format(indt_dict[k], objname)

            ratio = jsonpath.jsonpath(data_sets[k], "$..contrast.history")
            timeT    = digitalConfig.getdatelist(start=last_day,
                                                 between=len(ratio[0]),
                                                 reverse=True)
            yield {"objname":"行业大盘:{}:{}:{}".format(indt_dict[k], indt_dict[1], objname),
                   "data":dict(zip(timeT, ratio[0])),
                   'unit':"%",
                   'cat':cat}

            data  = jsonpath.jsonpath(data_sets[k], "$..index.history")
            timeT    = digitalConfig.getdatelist(start=last_day,
                                                 between=len(data[0]),
                                                 reverse=True)
            yield {"objname":"行业大盘:{}:{}:{}".format(indt_dict[k], indt_dict[0], objname),
                   "data":dict(zip(timeT, data[0])),
                   "unit":"",
                   "cat":cat}

    def Conn(self):
        return self._Mconn



def GenSeed(code, name=None):
    sql = "SELECT seed,seed_val FROM `t_ext_seed_data`" \
          " WHERE `platform` = 'Alizs' AND `pseed` = '%s'"%code
    conn= mysqlAssist.immysql()
    for i in conn.query(sql):
        yield i


def process(code,name):
    for i in GenSeed(code):
        objname = "%s:%s"%(name,i[1])
        for k in p.parse_menu(cat=i[0], objname=objname):
            k['freq'] = 2
            k['mode'] = {"cat":k['cat'],"mode":"A"}
            ep.loadSQL(k)
        process(i[0], objname)


if __name__ == '__main__':
    from middles.middleWare import EasyUploadMenu
    p = AliInd(open_sql=True)
    ep = EasyUploadMenu.uploadMenu(
        conn=p.Conn(),
        plat=7,
        channel="阿里指数",
        prefix="AL"
    )
    ep.setChannelCode("Alizs")
    # res = p.Request(p.start_urls, None)
    # p.parse_url(response=res, layer=1)

    process(0,"频道")
    # for i in p.parse_menu(cat='1033199', objname="Thisrt"):
    #     ep.loadSQL(i)
