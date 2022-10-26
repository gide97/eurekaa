'''
    __author__ = 'gnugroho'

    [S]uper
    [U]sefull
    [S]qlite3
    [H]elper
    [I]mplementation
'''


import sqlite3
import os
import json
# from os import sync # pylint: disable=no-name-in-module
from os import fsync

class sushiWrapper(object):
    def __init__(self):
        pass
    def open(self, dbfile):
        self.db = sqlite3.connect(dbfile,detect_types=sqlite3.PARSE_DECLTYPES)
        self.f = open(dbfile,'r+')
        return self.db
    def createTable(self, tablename, rowname, rowdatatype):
        '''
        create new table. please provide table name, rowname in tuple, rowdatatype in tuple.
        all parameter are using string. rowname and rowdatatype count must equal.
        '''    
        sql1 = "CREATE TABLE IF NOT EXISTS " + tablename
        sql2 = "(id INTEGER PRIMARY KEY" 
        sql3 = ""
        for i in range(0,len(rowname)):
            if i == len(rowname) - 1:
                sql3 = sql3 + "," + rowname[i] + " " + rowdatatype[i] + ")"
                break
            sql3 = sql3 + "," + rowname[i] + " " + rowdatatype[i]
        sql=sql1+sql2+sql3
        # print(sql)
        self.db.execute(sql)
    def insert(self, tablename, rowname, rowdata):
        sql1 = "INSERT INTO " + tablename
        ln = len(rowname)
        if ln > 1:
            sql2 = "("
            sql3 = " values("
            for r in range(0,len(rowname)):
                if r == 0:
                    sql2 = sql2 + rowname[r]
                    sql3 = sql3 + "?"
                else:
                    sql2 = sql2 + "," + rowname[r]
                    sql3 = sql3 + ",?"
            sql2 = sql2 + ")"
            sql3 = sql3 + ")"
            sql1 = sql1 + sql2 + sql3
        else:
            sql1 = sql1 + "(" + rowname[0] + ") values(?)"
        # print(sql1)
        #print(rowdata)
        self.db.execute(sql1,rowdata)
    def insertOne(self, tablename, rowname, rowdata):
        '''
       insert one data to available table. the data tuple count must be equal with row count. 
        '''
        # print('sek sek')
        sql1 = "INSERT INTO " + tablename + str(rowname) + " values"
        sql2 = str(rowdata)
        sql=sql1+sql2
        # print(sql)
        self.db.execute(sql)
    def select(self, tablename, row = None, value = None, column = "*"):
        if type(row) is tuple:
            sql ="SELECT " + column + " from "+ tablename + " WHERE " + row[0] + "='" + value[0] + "'"
            # print(sql)
            for r in range(0,len(row)):
                if r == 0: pass
                else:
                    sql = sql + " AND " + str(row[r]) + "='" + str(value[r]) + "'"
        else:
            if row == None:
                sql ="SELECT " + column + " from "+ tablename
            else:
                sql = 'SELECT %s from %s WHERE %s = "%s"'%(column,tablename,row,value)
        data = self.db.execute(sql)
        result = []
        for i in data:
            result.append(i)
        return result 
    def selectWithCommand(self, tablename, command = None, column = "*", param = None, optionalFirstCommand = None):
        if command == None:
            sql = "SELECT " + column + " from " + tablename
        else:
            sql = "SELECT " + column + " from " + tablename + " " + command
        if optionalFirstCommand is not None:
            sql = optionalFirstCommand + " " + sql
        if param == None:
            data = self.db.execute(sql)
        else:
            data = self.db.execute(sql, param)
        result = []
        for i in data:
            result.append(i)
        return result
    def update(self, tablename, keySearch, valueSearch, keyTarget, valueTarget):
        '''
        tablename : table name
        keySearch : key in row to search for
        valueSearch : value to search for (in keySearch row)
        keyTarget : the key to be updated
        valueTarget : the value updated in key
        '''
        sql = "UPDATE "+ tablename +" SET " + keyTarget + "='" + valueTarget + "' WHERE " + keySearch + "='" + valueSearch +"'"
        # print(sql)
        self.db.execute(sql)
    def updateUnion(self, tablename, columnTarget, columnSearch, unionValue):
        sql = "UPDATE " + tablename + " SET"
        if type(columnTarget) is list or type(columnTarget) is tuple:
            for r in range(0,len(columnTarget)):
                comma = ", "
                if r == 0:
                    comma = " "
                sql = sql + comma + columnTarget[r] + " = ?"
        else:
            sql = sql + " " + columnTarget + " = ?"

        sql = sql + " WHERE " + columnSearch + " = ?"
        self.db.execute(sql, unionValue)
    def delete(self, tablename, keySearch = None, value = None):
        sql = "DELETE FROM " + tablename 
        if keySearch != None:
            sql = sql + " WHERE " + keySearch + "= ?"
            self.db.execute(sql, value)
        else:
            self.db.execute(sql)
    def isEmpty(self, tabelname):
        num = self.getLength(tabelname)
        if num == 0:
            empty = True
        else:
            empty = False
        return empty
    def getLength(self, tablename, cmd=None, param=None):
        sql = "SELECT COUNT(*) FROM " + tablename
        if cmd is not None:
            sql = sql + cmd
        if param is not None:
            dt = self.db.execute(sql, param)
        else:
            dt = self.db.execute(sql)
        try:
            ln = int(dt.fetchone()[0])
        except Exception:
            ln = 0
        return ln
    def commit(self, pwr=0, syc=True):
        if pwr <= 0: #if power ok
            self.db.commit()
            if syc is True:
                self.sync() #need to sync after commit
    def close(self):
        self.db.close()
    def deleteTable(self, tablename):
        self.db.execute("DROP TABLE IF EXISTS " + tablename)
    def execute(self, query):
        return self.db.execute(query)
    def sync(self):
        os.fsync(self.f)