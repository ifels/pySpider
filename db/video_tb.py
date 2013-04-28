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
        hashes = ";".join(video_info.qhash_list)
        DbBase.insert(self, self.tb_name,
                      title = video_info.title,
                      sub_title = video_info.sub_title,
                      hash = hashes,
                      img = video_info.img,
                      actors = video_info.actors,
                      director = video_info.director,
                      video_type = video_info.type,
                      area = video_info.area,
                      update_time = video_info.update_time,
                      public_time = video_info.public_time,
                      status = video_info.status,
                      brief = video_info.brief,
                      ref_url = video_info.ref_url,
                      )