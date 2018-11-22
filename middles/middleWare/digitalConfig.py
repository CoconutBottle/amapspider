#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import re
import datetime

def fuckAntiNum(strDate):
    """
    all use
    :param strDate:
    :return:
    """
    return re.sub("[^0-9]", "", strDate)

def KeepNum(data):
    """
    all use
    :param data:
    :return:
    """
    tmp = {}
    for i in data:
        if re.search("\d[.0-9]+", data[i]):
            tmp[i] = data[i]
    return tmp


def fuckMonthEnd(md="", d=0, **kwargs):
    """
    all use
    :param md:
    :param d:
    :param kwargs:
    :return:
    """
    import  calendar
    try:
        if md =="":raise ValueError
    except:
        year, month = int(kwargs["year"]), int(kwargs["month"])
        fday, eday = calendar.monthrange(year, month)
    else:
        md = re.sub("[^\-0-9]","-",md)
        if re.search("-", md):
            year, month = md.split("-")
            year, month = int(year), int(month)
        else:
            year = int(md)//100
            month= int(md)%100

        fday, eday = calendar.monthrange(year, month)


    if d == -1:return eday
    elif d == 0:return "%d-%02d-%02d"%(year, month, eday)
    elif d == 1:return fday
    else: return -1





def frequency2id(frq):
    """
    all use
    :param frq:
    :return:
    """
    frq = frq.decode("utf8", "ignore")
    if re.search("日|天|day".decode("utf8", "ignore"), frq):
        return 2
    elif re.search("week|周".decode("utf8", "ignore"), frq):
        return 3
    elif re.search("月|month".decode("utf8", "ignore"), frq):
        return 4
    elif re.search("季|season".decode("utf8", "ignore"), frq):
        return 5
    elif re.search("year|年".decode("utf8", "ignore"), frq):
        return 6
    else:
        return 100


def calculateDays(start, between, reverse=False):
    day = datetime.timedelta(days=1)
    if reverse:
        for i in range(-1*between+1,1):
            yield day*i+start
    else:
        for i in range(between):
            yield day*i+start


def getdatelist(start, end=None, **kwargs):
    """

    :param start: 开始日期
    :param end: 结束日期， 默认当前
    :param kwargs: between间隔日数， reverse 是否倒序
    :return:
    """
    try:
        between = kwargs['between']
    except:
        if end is None:
            end = datetime.datetime.now()
        else:
            end = datetime.datetime.strptime(end, "%Y-%m-%d")
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        dates = []
        for i in calculateDays(start=start, between=(end - start).days):
            dates.append(datetime.datetime.strftime(i,'%Y-%m-%d'))
        return dates
    else:
        try:reverse = kwargs['reverse']
        except:reverse = False
        dates = []
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        for i in calculateDays(start=start, between=between,
                               reverse=reverse):
            dates.append(datetime.datetime.strftime(i,'%Y-%m-%d'))
        return dates

if __name__ == '__main__':
    print(getdatelist(start='2018-11-10', between=3,reverse=True))