# -*- coding:utf-8 -*-

'''
Created on 2013-4-26
@author: niexinxin
'''
import Utils

def printf(args, kwargs):
    print(args, kwargs)

def printf(msg):
    msg = ('%s' %msg)
    msg = Utils.to_unicode(msg)
    print(msg)
