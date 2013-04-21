# -*- coding:utf-8 -*-


'''
Created on Apr 21, 2013

@author: douzifly
'''

import urllib2, urllib

class WebTool(object):

    @staticmethod
    def request(url, params = None, method = "get"):
        method = method.lower()
        if params != None:
            if method == "get":
                url = url + "?" + urllib.urlencode(params)
            elif method == "post":
                params = urllib.urlencode(params)
        print("geturl:%s, method:%s" % (url, method))
        
        req = urllib2.Request(url)
        try:
            if method == "get":
                resp = urllib2.urlopen(req)
            elif method == "post":
                resp = urllib2.urlopen(req, params)
            else: 
                return ""
            return resp.read()
        except Exception, e:
            print("error:", e)
            return ""

    

    
        