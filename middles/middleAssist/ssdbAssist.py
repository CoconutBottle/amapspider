#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import ssdb
from settings import SsdbHost
from sshtunnel import SSHTunnelForwarder

class SSDBsession(object):
    def __init__(self):
        self.ssdb = ssdb.SSDB(SsdbHost["host"], SsdbHost["port"])

    def connect(self):
        return self.ssdb

    def __del__(self):
        del self


class SshSSDB(SSDBsession):
    def __init__(self):
        server = SSHTunnelForwarder(
            ssh_address_or_host="14.17.121.132",
            ssh_password="2BB703181625B5F31",
            ssh_port=13389,
            ssh_username="zhangzhanming",
            remote_bind_address=("10.0.0.14", 7779)
        )
        server.start()
        print("test:", server.local_bind_port)
        self.ssdb = ssdb.SSDB(
            host="127.0.0.1",
            port=server.local_bind_port,
            charset='utf8')

tt = [
{'UM_distinctid':'1667fd1f2c439b-02718094f0fc62-43450521-1fa400-1667fd1f2c51e7; ',
'_ga':'GA1.2.1709393261.1539739819; ',
'cloud-anonymous-token':'6fdf5cc7dc2941f9a7f927039fa32331; ', '_gid':'GA1.2.740055224.1540542488; ',
'_gat':'1; '},
{'UM_distinctid':'1667fd1f2c439b-02718094f0fc62-43450521-1fa400-1667fd1f2c51e7; ',
'_ga':'GA1.2.66068986.1539742758; ',
'cloud-anonymous-token':'233be42c12f349a6aa0c3e12c4c9eabf; ', '_gid':'GA1.2.374061592.1541382800; ',
'_gat':'1; '},
{"cloud-anonymous-token":"233be42c12f349a6aa0c3e12c4c9eabf; ",
"UM_distinctid": "1667fd1f2c439b-02718094f0fc62-43450521-1fa400-1667fd1f2c51e7; ",
"_ga": "GA1.2.66068986.1539742758; ",
"_gid": "GA1.2.2074228101.1541142296; ",
"_gat": "1"}]

if __name__ == '__main__':
    import random, re
    p = SshSSDB().connect()
    with open("E:\\test\\account.txt", "r") as f:
        fr = f.readlines()
        B = []
        for i in fr:
            a = {}
            uname, phone, passwd = i.split(",")
            print(uname)
            a["cookie"] = random.choice(tt)
            a["account"] = [phone, re.sub("\n","",passwd)]
            p.hset("robo:accountInfo", uname, a)
            B.append(uname)
        p.set("robo:uname", B)
        print(B)
        f.close()
        del p
