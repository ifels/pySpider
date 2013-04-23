#coding: UTF-8

'''
Created on 2013-4-20

@author: niexinxin

Hakuzy类 用于采集http://www.hakuzy.com 网站上的快播资源
'''
import re
from Koala import Koala
from bs4 import BeautifulSoup
from video_info import Video_Info
from WebTool import WebTool
import time
import Config

class HakuzyVideoParser(object):
    
    
    def parse_search_page(self, html):
        '''
            解析搜索结果中的影片链接 可能有多个
            @author: douzifly
            @return: list(Video_Info) 只会填充 url_in_search
        '''

        matches = re.findall(u"影片链接开始代码(.*)影片链接结束代码", html)
        if not matches:
            return None
        videos = list()
        for match in matches:
            match = match.replace("-->//","").replace("<!--", "") # 不效率 
            print(match)
            v = Video_Info()
            v.url_in_search = "http://www.hakuzy.com/" + match
            videos.append(v)
            pass
        return videos
    
    def parse(self, soup, video_info):
        '''
            parse text to VideoInfo 
            @author:douzifly
            @param soup:
            @param video_info: Video_Info object to be filled  
        '''
        assert soup != None and video_info != None
        
        html = soup.get_text()
        #print html
        self.parse_title(html, video_info)
        self.parse_actors(html, video_info)
        self.parse_director(html, video_info)
        self.parse_type(html, video_info)
        self.parse_language(html, video_info)
        self.parse_area(html, video_info)
        self.parse_public_time(html, video_info)
        self.parse_update_time(html, video_info)
        self.parse_statues(html, video_info)
        self.parse_img(soup, video_info)
        self.parse_qhash_list(soup, video_info)
        pass
    
    def parse_title(self, html, video_info):
        match = re.search(u'影片名称开始代码(.*)影片名称结束代码', html)
        if match:
            video_info.title = match.group(1)
            print u"影片名称: %s" % match.group(1)
        
        match = re.search(u'影片副标开始代码(.*)影片副标结束代码', html)
        if match:
            video_info.sub_title = match.group(1)
            print u"影片副标: %s" % match.group(1)  
            

    def parse_actors(self, html, video_info):
        match = re.search(u'影片演员开始代码(.*)影片演员结束代码', html)
        if match:
            video_info.actors = match.group(1)
            print u"演员: %s" % match.group(1)
            
    
    def parse_director(self, html, video_info):
        match = re.search(u'影片导演开始代码(.*)影片导演结束代码', html)
        if match:
            video_info.director = match.group(1)
            print u"导演: %s" % match.group(1) 
            
    
    def parse_type(self, html, video_info):
        match = re.search(u'影片类型开始代码(.*)影片类型结束代码', html)
        if match:
            video_info.type = match.group(1)
            print u"影片类型: %s" % match.group(1)  
    
    def parse_language(self, html, video_info):
        match = re.search(u'影片语言开始代码(.*)影片语言结束代码', html)
        if match:
            video_info.language = match.group(1)
            print u"影片语言: %s" % match.group(1)          
    
    def parse_area(self, html, video_info):
        match = re.search(u'影片地区开始代码(.*)影片地区结束代码', html)
        if match:
            video_info.area = match.group(1)
            print u"影片地区: %s" % match.group(1)  
          
            
    def parse_public_time(self, html, video_info):
        match = re.search(u'上映日期开始代码(.*)上映日期结束代码', html)
        if match:
            video_info.public_time = match.group(1)
            print u"上映日期: %s" % match.group(1) 
            
    def parse_update_time(self, html, video_info):
        match = re.search(u'影片更新时间开始代码(.*)影片更新时间结束代码', html)
        if match:
            video_info.update_time = match.group(1)
            print u"更新时间: %s" % match.group(1)  
            
    def parse_statues(self, html, video_info):
        match = re.search(u'影片状态：(.*)', html)
        if match:
            video_info.status = match.group(1)
            print u"影片状态: %s" % match.group(1)        
            
    def parse_brief(self, html, video_info):
        match = re.search(u'影片介绍开始代码(.*)影片介绍结束代码', html)
        if match:
            video_info.brief = match.group(1)
            print u"影片介绍: %s" % match.group(1)    
            
    def parse_img(self, soup, video_info):
        img = soup.find('img', onerror=True)
        if img:
            video_info.img = img.get('src')
            print u'img = %s' % (img.get('src'))
    
    def parse_qhash_list(self, soup, video_info):
        for input_area in soup.find_all('input'):
            vaule = input_area.get('value')
            if vaule.lower().startswith("qvod:"):
                video_info.qhash_list.append(vaule);

class Hakuzy(Koala):
    def __init__(self, webSiteURL, entryFilter=None, yieldFilter=None, identifier=None, enableStatusSupport=False):
        Koala.__init__(self, webSiteURL, entryFilter, yieldFilter, identifier, enableStatusSupport)
        self.__total_size = 0
        self.video_list = list()
        self.video_parser = HakuzyVideoParser()
        print "Hakuzy.__init__"
    
    def parse(self, soup):
        #print html
        if not soup:
            print("ERROR:soup is None")
            return
        
        print  u"#####################"
        video_info = Video_Info()
        self.video_parser.parse(soup, video_info)
        
        for qhash in video_info.qhash_list:
            print qhash
            
        if len(video_info.qhash_list) > 0:
            self.video_list.append(video_info)
                
def start_crawl():  
    '''
         只允许进入www.hakuzy.com/list/和 www.hakuzy.com/detail/ 这样的URL中，并只抓取URL以.html结尾的URL
    '''
    entryFilter = dict()
    entryFilter['Type'] = 'allow'
    entryFilter['List'] = [r'www\.hakuzy\.com/list/', r'www\.hakuzy\.com/detail/', ]

    yieldFilter = dict()
    yieldFilter['Type'] = 'allow'
    yieldFilter['List'] = [r'www\.hakuzy\.com/detail/.*\.html$', ]


    hakuzy = Hakuzy("http://www.hakuzy.com/", entryFilter, yieldFilter);
    #hakuzy = Hakuzy("www.hakuzy.com/detail/?47931.html", entryFilter, yieldFilter, enableStatusSupport=False);
    for url in hakuzy.go(10):
        #print url
        time.sleep(Config.NETWORK_REQUST_INTERVAL);
        pass
    
def search(keyword):
    ''' 
        search content for keyword
        @author: douzifly
    '''
    if not keyword:
        return
    url = "http://www.hakuzy.com/search.asp"
    params = {"searchword": keyword.encode("gbk")}
    html = WebTool.request(url, params, "post") # replace with other lib
    if not html:
        print("ERROR:cant get html")
        return
    html = html.decode("gbk")
    print(html) # this html only contain search result, no hash
    parser = HakuzyVideoParser() # do not create parse every time
   
    # find video links
    videos = parser.parse_search_page(html)
    if not videos:
        return 
    
    for video in videos:
        html = WebTool.request(video.url_in_search)
        if not html:
            continue
        html = html.decode("gbk")
        soup = BeautifulSoup(html)
        video_info = Video_Info()
        parser.parse(soup, video_info)
        print("###################")
        print(video_info)

    pass
    
if __name__ == "__main__":
    start_crawl()
    #test_parse()
    #search("北京遇上西雅图")

