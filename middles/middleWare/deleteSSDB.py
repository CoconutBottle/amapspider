#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from middles.middleAssist import ssdbAssist

DEFAULT_KEY = "s_o_d_i_{}"
sdb = ssdbAssist.SSDBsession().connect()

def delRange(*args):
    for i in range(args[0], args[1]):
        sdb.hclear(DEFAULT_KEY.format(i))
        print(DEFAULT_KEY.format(i), " delete Successfully!")

if __name__ == '__main__':
    delRange(1161232, 1161407)