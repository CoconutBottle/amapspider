#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("/root/iimedia_data")

from  sqlalchemy import create_engine



from settings import MysqlHost

class Msession(object):
    def __init__(self):
        print(
            "mysql+mysqlconnector://%s:%s@%s:%d/%s?charset=UTF-8"%(MysqlHost["user"],
                                              MysqlHost["passwd"],
                                              MysqlHost["host"],
                                              MysqlHost["port"],
                                              MysqlHost["db"])
        )
        self.mysql_engine = create_engine(
            "mysql://%s:%s@%s:%d/%s?charset=utf8"%(MysqlHost["user"],
                                              MysqlHost["passwd"],
                                              MysqlHost["host"],
                                              MysqlHost["port"],
                                              MysqlHost["db"]),
            max_overflow=5
        )
        self.opened = False


    def execute(self,sql, param=None):
        if self.opened == False:
            self.conn = self.mysql_engine.connect()

        if param is None:
            tt = self.conn.execute(sql)
        else:
            tt = self.conn.execute(sql, param)
        if self.opened:
            self.opened = False
            self.conn.close()
        return tt


    def insert(self, tbName,**kwargs):

        try:
            if self.opened == False:
                self.opened = True
                self.conn = self.mysql_engine.connect()

            data_values = "(" + "%s," * (len(kwargs)) + ")"
            data_values = data_values.replace(',)', ')')

            dbField = kwargs.keys()
            dataTuple = tuple(kwargs.values())
            dbField = str(tuple(dbField)).replace("'", '')

            sql = """insert ignore into %s %s values %s """ % (tbName, dbField, data_values)
            params = dataTuple
            # print(sql)
            self.conn.execute(sql, params)

        except Exception as e:
            print e
        finally:
            if self.opened :
                self.conn.close()
                self.opened = False



if __name__ == '__main__':
    p = Msession()
    p.execute("select * from t_event")
    for i in p.execute("select * from t_event"):
        print(i)