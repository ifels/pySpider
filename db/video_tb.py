#coding:utf-8

'''
Created on Apr 25, 2013
操作视频表
@author: douzifly
'''

from db_base import DbBase

class VideoTb(DbBase):

    def __init__(self):
        DbBase.__init__(self)
        self.tb_name = "tb_video"
    
    def insert(self, video_info):
        hashstr = ""
        for hash in video_info.qhash_list:
            hashstr += hash + ";"
        DbBase.insert(self, self.tb_name,
                            title = video_info.title,
                            hash = hashstr,
                            img = video_info.img,
                            sub_title = video_info.sub_title
                            )