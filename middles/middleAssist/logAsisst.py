#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
from logging.handlers import RotatingFileHandler
import sys
class imLog(object):
    def __init__(self, filename):
        # 创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # Log等级总开关
        filename = "./logs/" + '%s.log' % filename
        fh = logging.handlers.RotatingFileHandler(filename, maxBytes=1024 * 1024 * 1, backupCount=20)
        # 创建一个handler，用于写入日志文件
        datefmt = '%Y-%m-%d %H:%M:%S'
        format_str = '%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d] %(message)s '
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        formatter = logging.Formatter(format_str, datefmt)
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def __call__(self, *args, **kwargs):
        return self.logger
        # logging.handlers.RotatingFileHandler('F:/Logs/%s.log'%rq,maxBytes=1024*1024,backupCount=40)

    # def debug(self,msg):
    #     self.logger.debug(msg)
    #
    # def info(self,msg):
    #     self.logger.info(msg)
    #
    # def error(self,msg):
    #     self.logger.error(msg)
