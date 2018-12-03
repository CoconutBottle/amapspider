#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
import digitalConfig
import re



def fuckAntiNum(strDate):
    """
    all use
    :param strDate:
    :return:
    """
    digitalConfig.fuckAntiNum(strDate)


def KeepNum(data):
    """
    all use
    :param data:
    :return:
    """
    digitalConfig.KeepNum(data)



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
    digitalConfig.frequency2id(frq)

def cookiesSmooth(cookies):
    """
    all use
    :param cookies:
    :return:
    """
    s = ""
    for i in cookies.keys():
        tmp = i+"="+cookies[i]
        s += tmp
    return s

import urllib2
import urllib
import cookielib

def loginWeb(user_data, loginurl):
     """
     undefine
     :param user_data:
     :param loginurl:
     :return:
     """
     data=user_data  #登陆用户名和密码
     post_data=urllib.urlencode(data)   #将post消息化成可以让服务器编码的方式
     cj=cookielib.CookieJar()   #获取cookiejar实例
     opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
     #自己设置User-Agent（可用于伪造获取，防止某些网站防ip注入）
     headers ={"User-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
     website = loginurl
     req=urllib2.Request(website,post_data,headers)
     content=opener.open(req)
     print content.read()    #linux下没有gbk编码，只有utf-8编码
     for index, cookie in enumerate(cj):
         print '[', index, ']', cookie;

def login(url, cookies, user_data):
    """
    only Robo use
    :param url:
    :param cookies:
    :param user_data:
    :return:
    """
    import requests, settings
    url = url
    ct = requests.post(url=url, data=user_data,proxies=settings.ipProxy,
                       headers={"user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})
    cj = ct.cookies.get_dict()
    for k in cj.keys():
        cookies[k] = "%s; " % cj[k]

    return cookies



def RepeatLogin(url, cookies, user_data):
    ck = login(url, cookies, user_data)
    return cookiesSmooth(ck)


def RoboEasyLogin(key,mode=1):
    """
    only Robo Use
    :param key:
    :param mode:
    :return:
    """
    if mode == 0:
        from middles.middleAssist import redisAsisst
        Rs = redisAsisst.imredis().connection()
        userinfo = eval(Rs.hget("robo:accountInfo", key))
    elif mode == 1:
        from middles.middleAssist import ssdbAssist
        Rs = ssdbAssist.SSDBsession().connect()
        userinfo = eval(Rs.hget("robo:accountInfo", key))
    else:
        raise  ValueError("mode is incorrect! it must be 1 or 0")
    user_data = {
    "username": userinfo["account"][0],
    "password": userinfo["account"][1],
    "rememberMe": "false",
    "app": "cloud"}
    cookies = userinfo["cookie"]
    loginurl = "https://app.datayes.com/server/usermaster/authenticate/v1.json"
    ck = login(url=loginurl, cookies=cookies, user_data=user_data)
    ck = cookiesSmooth(ck)
    Rs.hset("tmpaddress:cookie", key, ck)

def getCookie(key, mode=1):
    if mode == 0:
        from middles.middleAssist import redisAsisst
        Rs = redisAsisst.imredis().connection()
    elif mode == 1:
        from middles.middleAssist import ssdbAssist
        Rs = ssdbAssist.SSDBsession().connect()
    else:
        raise ValueError("mode is incorrect! it must be 1 or 0")
    tt = Rs.hget("tmpaddress:cookie", key)
    print("getCookie:", tt)
    return tt


def insert(tbName, **kwargs):
    try:

        data_values = "(" + "%s," * (len(kwargs)) + ")"
        data_values = data_values.replace(',)', ')')

        dbField = kwargs.keys()
        dataTuple = tuple(kwargs.values())
        dbField = str(tuple(dbField)).replace("'", '')
        sql = """insert ignore into %s %s values %s """ % (tbName, dbField, data_values)

        return sql % dataTuple
    except Exception as e:
        print e
        return 0



if __name__ == '__main__':
    a = { "2017-12-24": "745", "2017-12-23": "729", "2017-03-09": "-", "2017-12-21": "723", "2017-12-20": "741", "2017-03-08": "-", "2018-06-29": "595", "2018-06-28": "637", "2017-12-22": "732", "2017-05-23": "-", "2017-05-22": "-", "2017-05-21": "-", "2017-04-06": "-", "2017-04-07": "-", "2017-04-04": "-", "2017-04-05": "-", "2017-04-02": "-", "2017-04-03": "-", "2017-04-01": "-", "2017-08-28": "-", "2017-04-08": "-", "2017-04-09": "-", "2017-01-05": "-", "2017-01-04": "-", "2017-01-07": "-", "2017-01-06": "-", "2017-01-01": "-", "2017-03-05": "-", "2017-01-03": "-", "2017-01-02": "-"}
    print( KeepNum(a))