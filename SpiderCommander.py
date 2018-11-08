#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import traceback ,Ice
Ice.loadSlice("../util/gmqi.ice")
import GMQ
sys.path.append("../")
from util.gmqutil import sendMessagetoQueue
import signal
import json

from gevent.queue import Queue, Empty
import gevent.monkey
gevent.monkey.patch_socket()

from middles.middleAssist import logAsisst
from tubes import RoboTubes
from middles.middleWare import EasyMethod

EasyMethod.RoboEasyLogin("Robo")
QUEUE_IP = '10.0.0.6'
QUEUE_PORT = 22345
READ_QUEUE_NAME = 'iMqDataSnatch_luobo_d'
DATA_COLLECT_QUEUE_NAME = 'iMqIMDataCollect'
IMMQ_PROXY = 'gmqObjectId:tcp -h 10.0.0.6  -p 22345'

LOGGER_NAME = "RoboCrawlGetTask"
lg = logAsisst.imLog(LOGGER_NAME)()

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    ic.destroy()
    sys.exit(0)


def handlework(workconfig):
    count = 0
    n = workconfig['num']
    try:
        while True:
            count += 1
            try:
                taskitem = tasks.get(timeout=3)
                lg.info(taskitem)
                # initial Object
                # crawler = YGCrawler()
                # crawler.snatch_day(taskitem)
                crawler = RoboTubes.RoboTubes(logger=LOGGER_NAME)
                tmpItem = crawler.Tubes(taskitem)
                tmpMsgInfo = json.dumps(tmpItem, encoding="utf-8", ensure_ascii=True)
                lg.info('sendMsg: %s' % tmpMsgInfo)
                sendMessagetoQueue(tmpMsgInfo, DATA_COLLECT_QUEUE_NAME, IMMQ_PROXY)
            except Empty:
                gevent.sleep(0.05)
                continue
    except Exception as e:
        lg.info('unknown err process:%s' % (e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lg.info((exc_type, fname, exc_tb.tb_lineno))



def readwork(workconfig):
    global reader
    while 1:
        msglist0 = {}
        try:
            rst1, msglist = reader.readMessages(READ_QUEUE_NAME, msglist0)
        except Exception as e:
            lg.info('read msg err : %s' % e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lg.info((exc_type, fname, exc_tb.tb_lineno))

            gevent.sleep(5)
            id = Ice.InitializationData()
            if id.properties == None:
                id.properties = Ice.createProperties(sys.argv)
            if Ice.intVersion() > 30500:
                if not id.properties.getProperty("Ice.Default.EncodingVersion"):
                    id.properties.setProperty("Ice.Default.EncodingVersion", "1.0")
            ic = Ice.initialize(id)
            base = ic.stringToProxy('gmqObjectId:tcp -h %s  -p %s' % (QUEUE_IP,QUEUE_PORT))
            reader = GMQ.MsgQueuePrx.checkedCast(base)
            continue

        gevent.sleep(0.1)
        if len(msglist) == 0:
            gevent.sleep(0.5)
            continue

        for msg in msglist:
            print msg
            try:
                jsoninfo = json.loads(msg)
                print(jsoninfo)
                taskInfo = {
                    'task_id': jsoninfo['task_id'],
                    'plat_id': jsoninfo['plat_id'],
                    'obj_id': jsoninfo['obj_id'],
                    'obj_name': jsoninfo['obj_name'],
                    'obj_code': jsoninfo['obj_code'],
                    'obj_ext': jsoninfo['obj_ext'],
                    'create_time': jsoninfo['create_time'],
                    'task_send_time': jsoninfo['task_send_time'],
                    'sn': jsoninfo['sn'],
                    'mode': jsoninfo['mode']
                }
                tasks.put(taskInfo)
            except Exception as e:
                lg.info( 'unknown err process:%s' % (e))

def worker(workconfig):
    lg.info('workconfig:%s' % workconfig)
    mode = workconfig['mode']
    if mode == 0:
        handlework(workconfig)
    elif mode == 1:
        readwork(workconfig)


def asynchronous():
    workconfigs = [{'mode': 0, 'num': str(i)} for i in xrange(5)]
    readmsg_config = {
        'mode': 1,
        'num': 0
    }
    workconfigs.append(readmsg_config)

    threads = [gevent.spawn(worker, workconfig) for workconfig in workconfigs]
    gevent.joinall(threads)



if __name__ == '__main__':
    tasks = Queue(maxsize=40)

    id = Ice.InitializationData()
    if id.properties == None:
        id.properties = Ice.createProperties(sys.argv)
    if Ice.intVersion() > 30500:
        if not id.properties.getProperty("Ice.Default.EncodingVersion"):
            id.properties.setProperty("Ice.Default.EncodingVersion", "1.0")
    ic = Ice.initialize(id)
    base = ic.stringToProxy(IMMQ_PROXY)
    reader = GMQ.MsgQueuePrx.checkedCast(base)
    print reader

    if not reader:
        raise RuntimeError("Invalid proxy")

    signal.signal(signal.SIGINT, signal_handler)
    asynchronous()
    ic.destroy()
