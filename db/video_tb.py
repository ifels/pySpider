#coding:utf-8

'''
Created on Apr 25, 2013
操作视频biao
@author: douzifly
'''

from db_base import DbBase
from db_base import build_sql

class VideoTb(DbBase):

    def __init__(self):
        DbBase.__init__(self)
        self.tb_name = "tb_video"
    
    def insert(self, **kwds):
        sql = build_sql(self.tb_name, "insert", **kwds)
        if not sql:
            print("sql is none")
            return False
        ok = self.execute(sql)
        print("exec sql:%s, ok:%s" % (sql, ok))
    
        