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
from middles.middleWare import  EasyDecorate
from middles.middleWare import digitalConfig as dC
from kids import YienKids
import json, jsonpath
import re, time
from lxml import html




class TimeValueError(ValueError):
    pass
class LimitValueError(ValueError):
    pass

class Yien(iimediaBase):
    def __init__(self):
        super(Yien, self).__init__()
        ### 单日票房 、 趋势分析
        self.start_urls = (
            'http://www.cbooo.cn/BoxOffice/GetDayBoxOffice',
            'http://www.cbooo.cn/BoxOffice/getDayInfoData',
            'http://www.cbooo.cn/BoxOffice/getWeekInfoData',
            'http://www.cbooo.cn/BoxOffice/getWeekendInfoData',
            'http://www.cbooo.cn/BoxOffice/getMonthBox',
            'http://www.cbooo.cn/year',
            'http://www.cbooo.cn/boxOffice/GetYearInfo_f',
            'http://www.cbooo.cn/BoxOffice/getCBD',

        )
        self.greed = False

    @EasyDecorate.try_except_callself
    def Request(self,url, **kwargs):
        import urllib2
        import urllib
        import requests
        print(url)
        try:
            data = kwargs['data']
        except:
            data = None

        # del ipProxy.ipRandom['http']
        # handler = urllib2.ProxyHandler(proxies=ipProxy.ipRandom)
        # opener = urllib2.build_opener(handler)
        # urllib2.install_opener(opener)
        # print(">>", data)
        # if data is not None:
        #     data = urllib.urlencode(data)
        # req = urllib2.Request(url, data=data)
        # response = opener.open(req)
        # return response.read()
        if data is None :
            normal_url = url
        else:
            data_str = ""
            t = urllib.urlencode(data)

            normal_url = "%s?%s" % (url, t)
        print(normal_url)
        req = requests.get(    url=normal_url,
                               headers = {"User-Agent":userAgent.user_agent},
                               proxies = ipProxy.ipRandom,
                               timeout = 5)
        return req.content


    ## 单日票房大类（单日票房，趋势分析）
    def parseSingleday(self, url,  mode, **kwargs):

        item = YienItem()
        if mode == 1:
            contents = self.Request(url)
            for i in YienKids.mode1(contents, item):
                yield i
        elif mode == 0:
            data = kwargs['data']
            print(data)
            contents = self.Request(url, data=data)
            for i in YienKids.mode0(contents=contents, item=item, data=data):
                yield i

    def parseYear(self, url, mode, **kwargs):
        item = YienItem()
        if mode == 0:
            data = kwargs['data']
            contents = self.Request(url=url, data=data)
            for i in YienKids.modeY0(contents=contents, item=item, data=data):
                yield i

    def parse(self, mode):
        """

        :param mode: 0:单日票房;1:单日趋势分析;
                     2:单周票房;3:周末票房;
                     4:单月票房;5:年度票房;
                     6:年度首周票房;7:影院票房;
        :return:
        """
        isLoop = True

        if mode == 0:
            url = self.start_urls[0]
            data = {
                "num":-1,
                "d":int(time.time()*1000),
                "codename":"sdayoff"
            }
            print(data['d'])
            end = 8 if self.greed else 2
            for i in range(1,end):
                data['num'] = -1 * i
                gt = self.parseSingleday(url, mode=0, data=data)
                for i in gt:
                    yield i

        elif mode == 1:
            url = self.start_urls[1]
            gt = self.parseSingleday(url=url, mode=1)
            for i in gt:
                yield i

        elif mode == 2:
            url = self.start_urls[2]
            # timestamp = time.strptime("2018-11-26", "%Y-%m-%d")
            # timestamp = time.mktime(timestamp)
            timestamp = dC.get_week_anyday(N=1, D=1)
            data={
                "sdate":time.strftime("%Y-%m-%d", time.localtime(timestamp)),
                "d":timestamp*1000,
                "num":6,
                "codename":"sweek"
            }
            i = 0
            while isLoop:
                if self.greed == False:
                    isLoop = False
                timestp = timestamp - i*86400*7

                data['sdate'] = time.strftime("%Y-%m-%d", time.localtime(timestp))
                data['d'] = timestp*1000

                gt = self.parseSingleday(url=url, mode=0, data=data)
                for k in gt:
                    yield k
                i += 1

        elif mode == 3:
            url = self.start_urls[3]
            timestp = time.time()
            data={
                "selDate":"",
                "d":0,
                "num":0,
                "codename":"weekendoff"
            }
            w = 1
            while isLoop:
                if self.greed == False:
                    isLoop = False

                ts  = map(lambda x:dC.get_week_anyday(ts=timestp, N=x[0], D=x[1]),
                          [(w,5),(w,7),(w+1,5),(w+1,7)])
                date= map(lambda x:time.strftime("%Y-%m-%d", time.localtime(x)), ts)

                data['selDate'] =  '{}&{}|{}&{}'.format(*date)
                data['d']       = ts[1]*1000

                gt = self.parseSingleday(url=url, mode=0, data=data)
                for i in gt:
                    yield i
                w += 1

        elif mode == 4:
            url = self.start_urls[4]
            timestp = time.time()
            data= {
                "sdate":"",
                "d": "",
                "num": 0,
                "codename":"smonth"
            }
            ts = time.time()

            while isLoop:
                if self.greed == False:
                    isLoop = False
                begin_day = dC.get_month_begin(ts)
                data["sdate"] = time.strftime("%Y-%m-%d", time.localtime(begin_day))
                if data["sdate"] == '2008-01-01':
                    isLoop = False

                data["d"]     = begin_day * 1000
                gt = self.parseSingleday(url=url, mode=0, data=data)
                for i in gt:
                    yield i
                ts = begin_day - 86400

        elif mode == 5:
            url = self.start_urls[5]
            data = {
                'year':2018,
                'codename':"syear"
            }
            y = int(time.strftime("%Y",time.localtime(time.time())))
            while isLoop:
                if self.greed == False:
                    isLoop = False
                data['year'] = y
                gt = self.parseYear(url=url, mode=0, data=data)
                for i in gt:
                    yield i
                y = y - 1
                if y == 2007:
                    isLoop = False
        elif mode == 6:
            url = self.start_urls[6]
            data = {
                'year': None,
                'd': None,
                'num': 0,
                'codename': "syear"
            }
            y = int(time.strftime("%Y",time.localtime(time.time())))
            while isLoop:
                if self.greed == False:
                    isLoop = False
                data['year'] = y
                data['d']    = time.mktime(time.strptime("{}-01-15".format(y),
                                                         "%Y-%m-%d")) * 1000
                gt = self.parseSingleday(url=url, mode=0, data=data)
                for i in gt:
                    yield i
                y = y - 1
                if y == 2007:
                    isLoop = False
        elif mode == 7:
            url = self.start_urls[7]
            data = {
                'pIndex': None,
                'dt':None,
                'd': None,
                'num': 0,
                'codename': "cidayoff"
            }

            timestp = time.time() - 86400
            while isLoop:


                data['dt'] = time.strftime("%Y/%m/%d", time.localtime(timestp))
                if timestp < time.time() - 7 * 86400:
                    isLoop = False
                data['d']  = timestp * 1000
                for i in range(1,11):
                    data['pIndex'] = i
                    gt = self.parseSingleday(url=url, mode=0, data=data)
                    for k in gt:
                        yield k

                timestp = timestp - 86400











if __name__ == '__main__':
    data = {
        "num":-1,
        "d":1544061986938
    }
    p = Yien()
    for i in p.parse(3):
        print(i)
