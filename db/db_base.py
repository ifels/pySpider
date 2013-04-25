#-*- coding:utf-8 -*-

'''
Created on Apr 25, 2013
提供基础的数据库操作
@author: douzifly
'''
import MySQLdb

DBHOST   = "localhost"
DBUSER  = "root"
DBPWD   = "cdslxy86"
DBNAME  = "spiderdb"


def build_sql(tb_name, action, **kwds):
        sql = ""
        if action == "insert":
            sql = "insert into " + tb_name + " ("
            keys = ""
            values = ""
            for (k,v) in kwds.items():
                print k, v
                keys += k + ","
                values += "'" + v + "',"
            sql = sql + keys[:len(keys) - 1] + ") values (" + values[:len(values) -1 ] + ")"
            return sql.encode("utf-8")
        return None

class DbBase(object):
    
    def __init__(self):
        self._cursor = None
        self._conn = None
    
    def open(self):
        try:
            self._conn = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPWD, db=DBNAME)
            self._cursor = self._conn.cursor()
        except Exception as e:
            print(e)
            return False
        return True
    
    def close(self):
        if self._cursor:
            self._cursor.close()
            self._conn.close()
            
    def execute(self, sql):
        if self._cursor:
            try:
                self._cursor.execute(sql)
                return True
            except Exception as e:
                print("ERROR:" + e)
                return False
        return False
            
    def fetch(self, sql):
        if self._cursor:
            self._cursor.execute(sql)
            return self._cursor.fetchall()
        return False
    
   
    
    if __name__ == "__main__":
        print build_sql("tb_video", "insert", username = "douzfily", age = "26", like = "python")
        
