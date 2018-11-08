# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

local_db_config = {
    'host': '10.1.1.186',
    'port': '3600',
    'user': 'root',
    'passwd': 'iimedia',
    'db': 'iimedia_yq',
    'charset': 'utf8'
}

db_config = {
    'host': '10.0.0.6',
    'user': 'news_app',
    'passwd': 'ak2IbO0t9CeQDTY2',
    'db':'news_app',
    'charset':'utf8'
}
"""
db_config = {
    'host': '14.17.121.132',
    'user': 'newsapp',
    'passwd': 'jsnews_app160125',
    'db':'news_app',
    'charset':'utf8'
}
db_config_ex = {
    'host': '10.0.0.6',
    'user': 'news_app_ext',
    'passwd': 'WhyqzIodADvIuPoP',
    'port':'3400',
    'db':'news_app_ext',
    'charset':'utf8'
}
"""

db_config_ex = {
    'host': '10.0.0.10',
    'user': 'news_app_ext',
    'passwd': 'iimedia2015',
    'port':'3400',
    'db':'news_app_ext',
    'charset':'utf8'
}

db_config_bak = {
    'host': '10.0.0.7',
    'user': 'news_app',
    'passwd': 'HqCjHEddMSvkTuOw',
    'port':'3401',
    'db':'news_app',
    'charset':'utf8'
}

db_config_8 = {
    'host': '10.0.0.8',
    'user': 'news_app',
    'passwd': 'ak2IbO0t9CeQDTY2',
    'port':'3401',
    'db':'news_app',
    'charset':'utf8'
}

db_config_10 = {
    'host': '10.0.0.10',
    'user': 'news_app',
    'passwd': 'ak2IbO0t9CeQDTY2',
    'port':'3401',
    'db':'news_app',
    'charset':'utf8'
}
"""
db_config_10 = {
    'host': '10.0.0.7',
    'user': 'news_app',
    'passwd': 'HqCjHEddMSvkTuOw',
    'port':'3401',
    'db':'news_app',
    'charset':'utf8'
}
"""

db_config_yq = {
    'host': '10.0.0.11',
    'user': 'iimedia_user_yq',
    'passwd': 'YYIFDyXQz44EAFbX',
    'port':'3500',
    'db':'iimedia_yq',
    'charset':'utf8'
}

db_config_yq_ext = {
    'host': '10.0.0.11',
    'user': 'iimedia_user_yq',
    'passwd': '3dNhibaBwP3jObX4',
    'port':'3501',
    'db':'iimedia_yq_ext',
    'charset':'utf8'
}

db_config_zsff = {
    'host': '10.0.0.13',
    'user': 'news_app_ext',
    'passwd': 'iimedia2015',
    'port':'3400',
    'db':'iimediareport',
    'charset':'utf8'
}

db_config_iimedia_data = {
    'host': '10.0.0.14',
    'user': 'news_app_ext',
    'passwd': 'iimedia2015',
    'port':'3400',
    'db':'iimedia_data',
    'charset':'utf8'
}


# 初始化数据库连接:
#engine = create_engine('mysql+mysqlconnector://root:@:3306/spider')

engine_local = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s' % (local_db_config['user'],
                                                                  local_db_config['passwd'],
                                                                  local_db_config['host'],
                                                                  local_db_config['port'],
                                                                  local_db_config['db'],
                                                                  local_db_config['charset']), echo=False)

engine = create_engine('mysql://%s:%s@%s:3401/%s?charset=%s'%(db_config['user'],
                                                         db_config['passwd'],
                                                         db_config['host'],
                                                         db_config['db'],
                                                         db_config['charset']), echo=False)
engine_ex = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_ex['user'],
                                                         db_config_ex['passwd'],
                                                         db_config_ex['host'],
                                                         db_config_ex['port'],
                                                         db_config_ex['db'],
                                                         db_config_ex['charset']), echo=False)

engine_bak = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_bak['user'],
                                                         db_config_bak['passwd'],
                                                         db_config_bak['host'],
                                                         db_config_bak['port'],
                                                         db_config_bak['db'],
                                                         db_config_bak['charset']), echo=False)

engine_8 = create_engine('mysql://%s:%s@%s:3401/%s?charset=%s'%(db_config_8['user'],
                                                         db_config_8['passwd'],
                                                         db_config_8['host'],
                                                         db_config_8['db'],
                                                         db_config_8['charset']), echo=False)

engine_10 = create_engine('mysql://%s:%s@%s:3401/%s?charset=%s'%(db_config_10['user'],
                                                         db_config_10['passwd'],
                                                         db_config_10['host'],
                                                         db_config_10['db'],
                                                         db_config_10['charset']), echo=False)

engine_yq = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_yq['user'],
                                                         db_config_yq['passwd'],
                                                         db_config_yq['host'],
                                                         db_config_yq['port'],
                                                         db_config_yq['db'],
                                                         db_config_yq['charset']), echo=False)

engine_yq_ext = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_yq_ext['user'],
                                                                   db_config_yq_ext['passwd'],
                                                                   db_config_yq_ext['host'],
                                                                   db_config_yq_ext['port'],
                                                                   db_config_yq_ext['db'],
                                                                   db_config_yq_ext['charset']), 
								pool_size = 200, 
                                                                    pool_recycle = 3600,
									echo=False)

engine_zsff = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_zsff['user'],
                                                                   db_config_zsff['passwd'],
                                                                   db_config_zsff['host'],
                                                                   db_config_zsff['port'],
                                                                   db_config_zsff['db'],
                                                                   db_config_zsff['charset']),
                                                                pool_size = 200,
                                                                    pool_recycle = 3600,
                                                                        echo=False)

engine_iimedia_data = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s'%(db_config_iimedia_data['user'],
                                                                   db_config_iimedia_data['passwd'],
                                                                   db_config_iimedia_data['host'],
                                                                   db_config_iimedia_data['port'],
                                                                   db_config_iimedia_data['db'],
                                                                   db_config_iimedia_data['charset']),
                                                                pool_size = 200,
                                                                    pool_recycle = 3600,
                                                                        echo=False)


# 创建DBSession类型:
DBSession_local = sessionmaker(bind=engine_local)
DBSession = sessionmaker(bind=engine)
DBSession_ex = sessionmaker(bind=engine_ex)
DBSession_bak = sessionmaker(bind=engine_bak)
DBSession_8 = sessionmaker(bind=engine_8)
DBSession_10 = sessionmaker(bind=engine_10)
DBSession_yq = sessionmaker(bind=engine_yq)
DBSession_yq_ext = sessionmaker(bind=engine_yq_ext)
DBSession_zsff = sessionmaker(bind=engine_zsff)
DBSession_iimedia_data = sessionmaker(bind=engine_iimedia_data)

# 初始化redis数据库连接
Redis = redis.StrictRedis(host='10.0.0.6',port=6400,db=0)
Redis7 = redis.StrictRedis(host='10.0.0.7',port=6400,db=0)
Redis6401 = redis.StrictRedis(host='10.0.0.7',port=6401,db=0)
Redis12 = redis.StrictRedis(host='10.0.0.12',port=6402,db=0)
Redis9 = redis.StrictRedis(host='10.0.0.11',port=6500,db=0)
