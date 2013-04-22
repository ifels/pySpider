# -*- coding:utf-8 -*-

'''
Created on 2013-4-21

@author: niexinxin
'''

class Video_Info(object):
    def __init__(self):
        self.title = ''
        self.img = ''
        self.sub_title =''
        self.actors = ''
        self.director = ''
        self.type = ''
        self.language = ''
        self.area = ''
        self.update_time = ''
        self.public_time = ''
        self.status = ''
        self.brief = ''
        self.qhash_list = list()
        #搜索结果中的
        self.url_in_search = ''
    
    def __str__(self, *args, **kwargs):
        out = self.title+":"
        for qhash in self.qhash_list:
            out += qhash+","
        return out
    