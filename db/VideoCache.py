#coding:utf-8
#__author__ = 'douzifly'

from Cache import Cache
from video_tb import VideoTb
import Log


class VideoCache(Cache):

    def writeToPersistence(self, datas):
        # move to thread pool later
        Log.write_stdout("writeToPersistence len:%d", len(datas))
        videoTb = VideoTb()
        ret = videoTb.open()
        if not ret:
            Log.write_stdout("cant open db")
            return
        for i, video in enumerate(datas):
            videoTb.insert(video)
        videoTb.commit()
        videoTb.close()
        Log.write_stdout("write finished")
        pass
