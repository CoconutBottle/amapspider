#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
import requests
from middles.middlePool import userAgent, ipProxy
import jsonpath, json, random, time
## 基础爬虫类
scookie ="UM_distinctid=1667fd1f2c439b-02718094f0fc62-43450521-1fa400-1667fd1f2c51e7; _ga=GA1.2.66068986.1539742758; cloud-anonymous-token=233be42c12f349a6aa0c3e12c4c9eabf; _gid=GA1.2.1850678946.1540534614; cloud-sso-token=A5F4621C68EC2C40504EB3E57B1EDD35"

class iimediaBase(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.start_urls = "http://www.baidu.com"
        self.allow_domains = []
        self.login  = ""
        self.count  = 0



    def startRequest(self, url,  **kwargs):

        try:
            data = kwargs["data"]
        except:
            try:
                response = requests.get(url=url, proxies = ipProxy.ipRandom,
                                        timeout=60,
                              headers={"cookie":self.cookie, "user-agent":userAgent.user_agent})
                self.count = 0
            except Exception as e:
                print(e)
                if self.count > 5:
                    raise requests.ConnectTimeout
                self.count += 1
                self.startRequest(url=url, retries= 0)
            else: return  response

        else:
            try:
                response = requests.post(url=url, proxies=ipProxy.ipRandom,
                               data=data,
                               headers={"cookie":self.cookie, "user-agent":userAgent.user_agent})
                self.count = 0
            except Exception as e:
                print(e)
                if self.count > 5:
                    raise requests.ConnectTimeout
                self.count += 1
                self.startRequest(url=url, data=data, retries=0)
            else:
                return response

    def startLoginRequest(self):
        pass

    def retry(self, url, retries, func, code=None):
        responset = self.startRequest(url=url, retries=retries)
        responset = responset.content.decode("utf8", "ignore")
        responset = json.loads(responset)
        webcode = jsonpath.jsonpath(responset, "$..code")[0]
        # print(type(webcode))
        if webcode < 0 and retries < 3:
            if webcode == -403:
                self.cookie = self.login()
            p = random.randint(5, 15)

            print("ErrorCode %d :Sleep %d sec ..." % (webcode, p))
            time.sleep(p)
            func(retries=retries + 1, code=code)
        if retries == 3 and webcode < 0:
            raise ValueError("HTTPERROR OVER MAX RETRY TIME")
        print("SuccessCode %d " % webcode)
        return responset



if __name__ == '__main__':
    import os

    url = "https://app.datayes.com/server/usermaster/authenticate/v1.json"
    data = {
        "username":"13726566433",
        "password":"z20180517!",
        "rememberMe":"true",
        "app":"cloud"
    }
    headers = {

        "Host":"app.datayes.com",
        "Origin":"https://app.datayes.com",
        "Referer":"https://app.datayes.com/sign/?RelayState=https%3A%2F%2Frobor.datayes.com%2Fdashboard",
        "user-agent": userAgent.user_agent
    }
    ct = requests.post(url=url, data=data, headers = headers)
    s = ""
    for i in ct.cookies.get_dict().keys():
        s += "%s=%s; "%(i,ct.cookies.get_dict()[i])
    # url = "https://robo.datayes.com/v2/home"
    # req = requests.get(url)
    headers["Cookie"] = s
    print(ct.cookies.get_dict())
    ct = requests.get("https://gw.datayes.com/rrp_adventure/web/supervisor/macro/RRP1359129",
                      headers=headers)
    print(json.loads(ct.content))






