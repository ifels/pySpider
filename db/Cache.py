#coding:utf-8

import Log

class Cache(object):

    def __init__(self):
        self._maxSize = 5 #test value
        self._cachedItems = list()
        pass

    def setMaxSize(self, size):
        '''
        set max size of cache, when reached to max size, flush will be trigger automatic
        @param size:
        @return:
        '''
        self._maxSize = size
        pass

    def flush(self):
        '''
        write all data to persistence
        @return:
        '''
        if len(self._cachedItems):
            self.writeToPersistence(self._cachedItems)
            del self._cachedItems[:]
        pass

    def add(self, data):
        Log.write_stdout("cache add")
        self._cachedItems.append(data)
        max = self._maxSize
        size = len(self._cachedItems)
        if size == max - 1:
            Log.write_stdout("cache fill, write to persistence")
            self.writeToPersistence(self._cachedItems[:max])
            del self._cachedItems[:max]
        pass

    def writeToPersistence(self, datas):
        '''
        subclass should override this method
        @param datas: datas should be write to persistence
        @return:
        '''
        pass



