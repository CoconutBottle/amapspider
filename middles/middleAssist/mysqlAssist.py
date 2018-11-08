#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)

import pymysql
from settings import MysqlHost



class immysql(object):

    def __init__(self, db=None):
        if db is  None:
            db = MysqlHost["db"]
        self.conn = pymysql.connect(
            host=MysqlHost["host"],
            port=MysqlHost["port"],
            user=MysqlHost["user"],
            passwd=MysqlHost["passwd"],
            db=db,
            charset='utf8')

    def get_cursor(self):
        return self.conn.cursor()

    def executemany(self, sql, params=None):
        cursor = self.get_cursor()
        try:
            cursor.executemany(sql, params)
            self.conn.commit()
            affected_rows = cursor.rowcount
        except Exception as e:
            print(e)
            return 0
        finally:
            cursor.close()
        return affected_rows

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def query(self, sql, ret=True):
        cursor = self.get_cursor()
        try:
            cursor.execute(sql, None)
            result = cursor.fetchall()
        except Exception as e:
            return None
        else:
            pass
        finally:
            cursor.close()
        return result

    def insert(self, tbName, **kwargs):

        try:

            data_values = "(" + "%s," * (len(kwargs)) + ")"
            data_values = data_values.replace(',)', ')')

            dbField = kwargs.keys()
            dataTuple = tuple(kwargs.values())
            dbField = str(tuple(dbField)).replace("'", '')
            cursor = self.get_cursor()
            sql = """insert ignore into %s %s values %s """ % (tbName, dbField, data_values)
            params = dataTuple
            cursor.execute(sql, params)
            cursor.close()
            return 1
        except Exception as e:
            print e
            return 0

    def __del__(self):
        self.conn.close()

class bjxmysql(object):

    def __init__(self, host,port, user, passwd ,db=None):

        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            db=db,
            charset='utf8')

    def get_cursor(self):
        return self.conn.cursor()

    def executemany(self, sql, params=None):
        cursor = self.get_cursor()
        try:
            cursor.executemany(sql, params)
            self.conn.commit()
            affected_rows = cursor.rowcount
        except Exception as e:
            print(e)
            return 0
        finally:
            cursor.close()
        return affected_rows

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def query(self, sql, ret=True):
        cursor = self.get_cursor()
        try:
            cursor.execute(sql, None)
            result = cursor.fetchall()
        except Exception as e:
            return None
        else:
            pass
        finally:
            cursor.close()
        return result

    def insert(self, tbName, **kwargs):

        try:

            data_values = "(" + "%s," * (len(kwargs)) + ")"
            data_values = data_values.replace(',)', ')')

            dbField = kwargs.keys()
            dataTuple = tuple(kwargs.values())
            dbField = str(tuple(dbField)).replace("'", '')
            cursor = self.get_cursor()
            sql = """ replace into %s %s values %s """ % (tbName, dbField, data_values)
            params = dataTuple
            cursor.execute(sql, params)
            cursor.close()
            return 1
        except Exception as e:
            print e
            return 0

    def __del__(self):
        self.conn.close()
