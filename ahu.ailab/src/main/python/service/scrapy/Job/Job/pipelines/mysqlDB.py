# -*- coding: utf-8 -*-
__author__ = 'liuyang'
import MySQLdb

class myaqlSave(object):

    def __init__(self):
        pass

    def insertleaders(self,tx,item):
        tx.execute('insert into allleader(姓名,职位,链接,机构,简历,部门)values(%s,%s,%s,%s,%s,%s)',(item['name'],item['work'],item['url'],item['englishname'],item['resume'],item['department']))

