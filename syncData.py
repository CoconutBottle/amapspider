#-*-coding:utf-8-*-
import sys
sys.path.append("../../")
import json
import os
import re
import signal
reload(sys)
sys.setdefaultencoding('utf8')
from sys import argv
from config import DBSession_iimedia_data
import time
from pyssdb import *
import datetime

KEY_DATA_TIME_ROW_PRE = 'key_'
KEY_DATA_AMO_ROW_PRE = 'val_'
KEY_OBJ_DETAIL_INFO = 'o_d_i_'
KEY_SNATCH_OBJ_DETAIL_INFO = 's_o_d_i_'

IS_DEBUG = True

session = DBSession_iimedia_data()
if IS_DEBUG:
    ssdb_src = Client("10.1.0.253", 8888)
    ssdb_des = Client("10.1.0.253", 8888)
else:
    ssdb_src = Client("10.0.0.14", 7779)
    ssdb_des = Client("10.0.0.14", 7778)


def getObjs(mode):
    objlist = []
    sql = 'select sub.ext_obj_id as obj_id , sub.obj_id as des_obj_id, \
    ext_obj.`offset` \
from t_data_obj_subscribe as sub \
left join t_data_obj as obj \
on obj.id = sub.obj_id \
and obj.frequence_mode = %s \
left join t_ext_data_obj ext_obj \
on ext_obj.id = sub.ext_obj_id \
where obj.id IS NOT NULL' % mode

    tmpresult = session.execute(sql)
    for item in tmpresult:
        obj_id = item['obj_id']
        des_obj_id = item['des_obj_id']
        offset = item['offset']
        tmpobj = {}
        tmpobj['obj_id'] = obj_id
        tmpobj['des_obj_id'] = des_obj_id
        tmpobj['offset'] = offset
        objlist.append(tmpobj)
    return objlist


def getObjData(obj_id,des_time_t):
    # 查数据回来
    data = {}
    data['20180901'] = '2.59'
    data['20180902'] = '2.58'
    return


def reportMissEvent(des_obj_id, time_t):
    print 'reportMissEvent %s %s' % (des_obj_id,time_t)
    localTime = time.localtime(time.time())
    sql = 'insert into t_event (type,name,obj_code,time_t,create_time) values (%s,"%s","%s","%s","%s")' \
          % (0, '数据缺漏（抓取方）', des_obj_id, time_t, time.strftime("%Y-%m-%d %H:%M:%S",localTime))
    session.



def reportConflictEvent(des_obj_id, time_t, src_amo, des_amo):
    print 'reportConflictEvent %s %s %s %s' % (des_obj_id, time_t,src_amo,des_amo)
    localTime = time.localtime(time.time())
    sql = 'insert into t_event (type,name,obj_code,time_t,note,create_time) values (%s,"%s","%s","%s","%s_%s","%s")' \
          % (1, '数据冲突', des_obj_id, time_t, src_amo, des_amo, time.strftime("%Y-%m-%d %H:%M:%S", localTime))
    session.execute(sql)


def reportSnatchErrEvent(des_obj_id, type, name,time_t):
    print 'reportSnatchErrEvent %s %s %s' % (des_obj_id, type, time_t)
    localTime = time.localtime(time.time())
    sql = 'insert into t_event (type,name,obj_code,create_time,time_t) values (%s,"%s",%s,"%s","%s")' % (type, name, des_obj_id, time.strftime("%Y-%m-%d %H:%M:%S",localTime),time_t)
    session.execute(sql)


#同步缺少的，上报异常
def syncObjData(src_obj_id, des_obj_id, offset, des_time_t):
    src_data_dict = {}
    des_data_dict = {}
    need_data_dict = {}

    if not (offset == None or offset == 0):
        tmpdatetime = int(time.mktime(time.strptime(des_time_t, "%Y-%m-%d")))
        tmp_des_time = tmpdatetime - offset * 24 * 3600
        des_time_t=time.strftime("%Y-%m-%d", time.localtime(tmp_des_time))

    src_data_list = ssdb_src.hgetall('%s%s' % (KEY_SNATCH_OBJ_DETAIL_INFO, src_obj_id))

    tmp_count = len(src_data_list) / 2
    for i in xrange(tmp_count):
        src_data_dict['%s' % src_data_list[2*i]] = '%s' % src_data_list[2*i+1]

    sql = 'select obj_id,time_t,amo from t_ext_data_node where obj_id = %s' % (src_obj_id)
    src_data_list = session.execute(sql)
    for item in src_data_list:
        time_t = item['time_t']
        amo = item['amo']
        tmpdate = time_t.strftime("%Y-%m-%d")
        src_data_dict['%s' % tmpdate] = '%s' % amo

    des_data_list = ssdb_des.hgetall('%s%s' % (KEY_OBJ_DETAIL_INFO, des_obj_id))
    tmp_count = len(des_data_list)/2
    for i in xrange(tmp_count):
        des_data_dict['%s' % des_data_list[2*i]] = '%s' % des_data_list[2*i+1]

    print 'src_data_dict : %s' % src_data_dict
    print 'des_data_dict : %s' % des_data_dict
    print 'des_time_t : %s' % des_time_t

    if des_time_t != "" and '%s' % des_time_t not in src_data_dict:
        reportMissEvent(des_obj_id, des_time_t)

    for tmptime in src_data_dict:
        if tmptime not in des_data_dict:
            print 'sync %s %s %s' % (des_obj_id, tmptime, src_data_dict[tmptime])
            need_data_dict[tmptime] = src_data_dict[tmptime]
            ssdb_des.hset('%s%s' % (KEY_OBJ_DETAIL_INFO, des_obj_id), '%s' % tmptime, '%s' % src_data_dict[tmptime])
        else:
            if src_data_dict[tmptime] != des_data_dict[tmptime]:
                reportConflictEvent(des_obj_id, tmptime, des_data_dict[tmptime], src_data_dict[tmptime])

    des_data_list = ssdb_des.hgetall('%s%s' % (KEY_OBJ_DETAIL_INFO, des_obj_id))
    tmp_count = len(des_data_list) / 2
    for i in xrange(tmp_count):
        des_data_dict['%s' % des_data_list[2 * i]] = '%s' % des_data_list[2 * i + 1]

    print 'final des_data_dict : %s' % des_data_dict

    if des_time_t != "" and '%s' % des_time_t not in des_data_dict:
        reportSnatchErrEvent(des_obj_id, 2, "数据缺漏（展示方）", des_time_t)

if IS_DEBUG:
    mode = 4
    des_time_t = '2018-09-30'
else:
    mode = argv[1]
    des_time_t = argv[2]

# 0：分钟；1:小时；2：天；3：周；4：月；5：季度；6：年；100：看frequence
def mode_switch(mode):
    return {
        0: 1,
        1: 2,
        2: 3,
        3: 1,
        4: 2,
        5: 3,
        6: 1
    }.get(mode, -1)

obj_list = getObjs(mode)

print 'obj_list size : %d' % len(obj_list)

for obj in obj_list:
    obj_id = obj['obj_id']
    des_obj_id = obj['des_obj_id']
    offset = obj['offset']
    print '%s %s %s' % (obj_id,des_obj_id,des_time_t)
    syncObjData(obj_id, des_obj_id, offset, des_time_t)




