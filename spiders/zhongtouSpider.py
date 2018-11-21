#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import os
curUrl = os.path.dirname(__file__) # 获取当前路径
pareUrl= os.path.abspath(os.path.join(curUrl, os.pardir))
sys.path.append(pareUrl)

from BaseSpider import iimediaBase
from middles.middlePool import userAgent, ipProxy
from middles.middleWare import EasyDecorate, EasyMethod
from items import CommonItem
import re

class xpathRules(object):
    xunit = "//*[@id=\"Table\"]/thead/tr[2]/td/nobr/text()"
    xtime = "//*[@id=\"Table\"]/tbody/tr/td[2]/text()"
    xobj  = "//*[@id=\"Table\"]/thead/tr[1]/td/nobr"
    xdata = "//*[@id=\"Table\"]/tbody/tr/td[{}]/text()"

def giveme(response):
    pass



def giveCookie(method="set"):
    """

    :param method: set/get
    :return:
    """
    import requests
    from middles.middleAssist import ssdbAssist
    SDBconn = ssdbAssist.SSDBsession().connect()


    url = "http://www.macrodb.com/ztxh/xh3_pro.asp?ways=TQL1"
    if method == "set":
        print("Getting cookie...")
        ip  = {"https":ipProxy.ipRandom["https"]}
        req = requests.get(url=url, proxies=ip,
                   headers = {"user-agent":userAgent.user_agent})
        print("Getting cookie finish!")
        cookies = req.cookies.get_dict()
        for cookie in cookies:
            ck = "{}={}".format(cookie, cookies[cookie])
            print("setting... ", ck)
            SDBconn.set("ZhongTou:Cookie", ck)
            return ck
    elif method == "get":
        ck = SDBconn.get("ZhongTou:Cookie")
        print("getting... ", ck)
        return ck
    else:
        raise ValueError("no such method values! It must be 'set' or 'get'.")

def test():
    import requests
    url = "http://www.macrodb.com/ztxh/xh3_pro.asp?ways=TQL1"
    ip  = {"https":ipProxy.ipRandom["https"]}
    req = requests.get(url=url, proxies=ip,
                       headers = {"user-agent":userAgent.user_agent})
    print(req.cookies.get_dict())

class ZhongTou(iimediaBase):
    def __init__(self, greed = True):
        super(ZhongTou, self).__init__()
        self.start_urls = "http://www.macrodb.com/ztxh/xh3_pro.asp?ways=TQL1"
        self.headers = {
            'cookie': giveCookie('get'),
            'user-agent':userAgent.user_agent,
        }
        del ipProxy.ipRandom['http']
        self.proxies = ipProxy.ipRandom
        self.urls = []
        self.channelname = []



    def auto_crawl(self):
        self.Request(url=self.start_urls, method="GET", callback=self.parse)
        return self.urls

    @EasyDecorate.try_except
    def Request(self, url, method, callback, count = 0, **kwargs):
        import urllib2

        proxies = urllib2.ProxyHandler(self.proxies)
        opener  = urllib2.build_opener(proxies)
        urllib2.install_opener(opener)
        if method == "GET" or method == "get":
            req     = urllib2.Request(url=url, headers=self.headers)
            contents= urllib2.urlopen(req).read().decode("gb2312")

            if len(contents) < 1000 and count < 4 \
                    and str(callback) == "self.parse_item":
                self.headers =  {
                    'cookie': giveCookie('set'),
                    'user-agent':userAgent.user_agent,
                }
                self.Request(url=url, method=method,
                             callback=callback, count=count+1)
            elif count > 3 and len(contents) < 1000 \
                    and str(callback) == "self.parse_item":
                raise StandardError("cookie无效; \t已经超过最大尝试次数")
            if callback == None:
                return contents
            else:
                callback(contents)
        elif method == "MOD" or method == "mod":
            from selenium import webdriver
            import time
            driver = webdriver.PhantomJS()
            driver.get(url)

            print(driver.get_cookies())
            time.sleep(1)
            contents = driver.page_source
            print("mod:", contents)
            callback(contents)
        else:
            raise ValueError("No such method.")

    @EasyDecorate.try_except
    def parse(self, response):
        from lxml import html
        modify_url = 'http://www.macrodb.com:8000/data_m/m_hg1/frmdiv.asp?ways={}&dr=m_hg1'
        tree = html.fromstring(response)
        code_sets = tree.xpath("//td[@bgcolor=\"#669ace\"]/@onclick")
        name_sets = tree.xpath("//td[@bgcolor=\"#669ace\"]")
        name_sets = map(lambda x:"".join(x.xpath("string()").split()), name_sets)

        for i, k in zip(code_sets,name_sets):
            self.channelname.append(k)
            suffix = re.search("ways=(.+?)'", i).group(1)
            fake_url = modify_url.format(suffix)
            self.Request(url=fake_url, method="GET", callback=self.parse_item)


    def parse_item(self, response):

        from bs4 import BeautifulSoup
        import urlparse

        compare_url = 'http://www.macrodb.com:8000/data_m/xx/xx'
        soup = BeautifulSoup(response, "html.parser")
        tags = soup.select("frame")
        fake_url = tags[-1]['src']
        t = urlparse.urljoin(compare_url,fake_url)
        self.urls.append(t)
        # yield t


    def parse_detail(self, url, specify = 0, **kwargs):
        """

        :param url:
        :param specify: 1:针对特定指标名进行爬取，0：否
        :return:
        """
        from lxml import html
        item = CommonItem.commonItem()
        if specify not in (1,0):
            raise ValueError("no such specify values! It must be 1 or 0")
        response = self.Request(url=url, method='GET', callback=None)
        tree = html.fromstring(response)
        time_list = tree.xpath(xpathRules.xtime)
        time_list = map(EasyMethod.fuckMonthEnd, time_list)

        objname   = tree.xpath(xpathRules.xobj)[1:]
        objname   = map(lambda x:x.xpath("string()"), objname)

        unit      = tree.xpath(xpathRules.xunit)
        unit      = map(lambda x:re.sub(r"[\[\]]", "", x), unit)
        print(unit)
        if specify:
            obj_num = dict(zip(objname, range(len(objname))))

            nums     = [obj_num[kwargs['objname'].split(":")[-1].decode("utf8")]]
            del obj_num
        else:
            nums = range(len(objname))


        for n in nums:
            value = tree.xpath(xpathRules.xdata.format(n+3))
            data = EasyMethod.KeepNum(dict(zip(time_list, value)))
            item.data = data

            if specify == 1:
                item.objname = kwargs['objname']
            else:
                item.objname ="中国投资频道:"+kwargs['channelname']+":"+objname[n]

            item.unit = unit[n]
            item.plat = 6
            item.freq = 4
            item.mode  = {"mode":1,
                          "url":url,
                          "name":item.objname}
            print(item())
            yield item()










if __name__ == '__main__':
    url = 'http://www.macrodb.com:8000/data_m/prg/showdata.asp?ffrm=1&prg=tab&rnd1=.8141141'
    # giveCookie('set')
    # p = ZhongTou(True)
    # p.auto_crawl()
    giveCookie('set')