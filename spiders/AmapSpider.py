#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

from BaseSpider import iimediaBase

class Amap(iimediaBase):

    def __init__(self):
        start_urls = [
            "http: // report.amap.com / ajax / getCityInfo.do?"
        ]
