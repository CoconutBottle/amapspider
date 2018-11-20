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
from middles.middleWare import EasyDecorate
import re


def giveme(response):
    pass



def giveCookie():
    from selenium import webdriver
    url = "http://www.macrodb.com/ztxh/xh3_pro.asp?ways=TQL1"
    print("running PhantomJS...")
    print("Getting cookie...")
    driver = webdriver.PhantomJS()
    driver.get(url)
    print("Getting cookie finish!")
    cookies = driver.get_cookies()
    for cookie in cookies:
        ck = "{}={}".format(cookie['name'], cookie['value'])
        print(ck)
        return ck

class ZhongTou(iimediaBase):
    def __init__(self, greed = True):
        super(ZhongTou, self).__init__()
        self.start_urls = "http://www.macrodb.com/ztxh/xh3_pro.asp?ways=TQL1"
        self.headers = {
            'cookie': "ASPSESSIONIDQASACACS=NHEFICKBFFFCGGEMBKFKENPL",
            'user-agent':userAgent.user_agent,
        }
        del ipProxy.ipRandom['http']
        self.proxies = ipProxy.ipRandom
        if greed:
            self.Request(url=self.start_urls, method="GET", callback=self.parse)


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
                    'cookie': giveCookie(),
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

        for i in tree.xpath("//td[@bgcolor=\"#669ace\"]/@onclick"):
            suffix = re.search("ways=(.+?)'", i).group(1)
            fake_url = modify_url.format(suffix)
            self.Request(url=fake_url, method="GET", callback=self.parse_item)

    @EasyDecorate.try_except
    def parse_item(self, response):

        from bs4 import BeautifulSoup
        import urlparse

        compare_url = 'http://www.macrodb.com:8000/data_m/xx/xx'
        soup = BeautifulSoup(response, "html.parser")
        tags = soup.select("frame")
        fake_url = tags[-1]['src']
        t = urlparse.urljoin(compare_url,fake_url)
        self.parse_detail(t)


    def parse_detail(self, url):
        from bs4 import BeautifulSoup
        response = self.Request(url=url, method='GET', callback=None)
        soup = BeautifulSoup(response, "html.parser")




if __name__ == '__main__':
    url = 'http://www.macrodb.com:8000/data_m/prg/showdata.asp?ffrm=1&prg=tab&rnd1=.8141141'
    p = ZhongTou(True)
    # p.Request(url=url, method="get" , callback=giveme)

