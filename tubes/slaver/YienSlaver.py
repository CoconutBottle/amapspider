#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import json, jsonpath

eng2chi = {
    "people":"人次",
    "sumboxoffice":"总票房(万)",
    "soffice":"单天票房(万)",
    "wom":"口碑",
    "ratio":"环比(%)"
}


def whatsField(**kwargs):
    if kwargs['mode'] == "0" or kwargs['mode'] == "3":
        field = ['AvpPeoPle', 'SumBoxOffice', 'BoxOffice',
                 'WomIndex', 'BoxOffice_Up']
    elif kwargs['mode'] == "1":
        field = ["AudienceCount", "Price", "BoxOffice",
                 "ShowCount"]
    elif kwargs['mode'] == "2":
        field = ['WomIndex', 'People', 'WeekAmount', 'SumWeekAmount',
                 'AvgPeople']
    elif kwargs['mode'] == "4":
        field =['avgboxoffice', 'avgshowcount', 'boxoffice',
                'WomIndex', 'box_pro']
    elif kwargs['mode'] == "5":
        field =["SumBoxoffice", "avgAudience","avgPrice"]
    elif kwargs['mode'] == "6":
        field = ['BoxOffice_Pro', 'BoxOffice', 'AvgPeople']
    elif kwargs['mode'] == "7":
        field = ['TodayShowCount', 'price', 'AvgPeople',
                 'Attendance', 'TodayBox', 'TodayAudienceCount',
                 'RowNum']
    else:
        field = -1
    return field


# 电影参数
def Ripper(ssdbconn, **kwargs):
    name = "crawl_8_{}_{}".format(kwargs['mode'], kwargs['tid'])
    field = whatsField(mode=kwargs['mode'])

    hg = ssdbconn.hgetall(name)
    hk = hg.keys()
    timeT = []
    t = { }



    for i in hk:
        movieInfo = eval(hg[i].decode("utf8"))
        timeT.append(i)
        for k in field:
            try:
                if t[k]:
                    t[k].append(movieInfo[k])

            except:
                t[k] = []
                t[k].append(movieInfo[k])



    for i in t:
        print(i)
        yield {
            "objname":"{}_{}".format(i, kwargs['mode']),
            "data":zip(timeT, t[i]),
            "ext":{"type":kwargs['mode'], 'field':i}
        }


