#coding: UTF-8

'''
Created on 2013-4-23

@author: niexinxin

'''

from __future__ import print_function
from bs4 import UnicodeDammit
import re
import sys
import hashlib
import Config
import requests
import time
import urlparse
import tldextract

# UTF-8字符集标准命名
UTF8_CHARSET_NAME = 'UTF-8'


def hash(text):
    '''
    生成字符串的哈希值（加简单salt）
    哈希值为“字符串的md5+长度值字符串的md5”的md5

    @param text: 要计算哈希值的文本
    @type text: 字符串

    @return: 十六进制形式的哈希值
    @rtype: 字符串
    '''
    textMD5 = hashlib.md5(text).hexdigest()
    textLengthMD5 = hashlib.md5(str(len(text))).hexdigest()

    return hashlib.md5(textMD5 + textLengthMD5).hexdigest()


def to_unicode(byteSequence):
    '''
    转换字节序列到unicode字符串

    @param byteSequence: 字节序列
    @type byteSequence: py3下为字节串，py2下为str字符串

    @return: unicode字符串
    @rtype: 字符串
    '''
    # 如果已经是unicode则直接返回
    if isinstance(byteSequence, unicode):
        return byteSequence
    else:
        # 尝试从中查找charset的html文本，针对html文本的unicode转换可大幅加速
        charsetPattern = r'''charset\s*=\s*['"]?([-\w\d]+)['"]?'''
        find = re.search(charsetPattern, byteSequence, re.I)
        if find:
            if find.group(1):
                try:
                    return byteSequence.decode(find.group(1), 'ignore')
                except Exception as error:
                    write_stderr(repr(error))
        # 上述方法均不成功，则使用bs4内置的unicode转换装置
        dammit = UnicodeDammit(byteSequence)
        return dammit.unicode_markup


def unicode_to(unicodeString, charset):
    '''
    转换unicode字符串到字节序列

    @param unicodeString: unicode字符串
    @type unicodeString: 字符串
    @param charset: 希望转换到字节序列的字符集
    @type charset: 字符串

    @return: 字节序列
    @rtype: py3下为字节串，py2下为str字符串
    '''
    if not isinstance(unicodeString, unicode):
        raise TypeError('Parameter "unicodeString" is not unicode type')
    else:
        return unicodeString.encode(charset, 'ignore')


def write_stdout(text):
    '''
    写文本到标准输出

    @param text: 文本
    @type text: 字符串

    @return: 无
    '''
    print(text, file = sys.stdout)


def write_stderr(text):
    '''
    写文本到标准错误输出

    @param text: 文本
    @type text: 字符串

    @return: 无
    '''
    print(text, file = sys.stderr)


def get_url_html(url):
    '''
    获取url的html超文本

    @param url: url地址
    @type url: 字符串

    @return: 成功则返回html，失败则触发异常
    @rtype: 字符串
    '''
    # 自定义header
    customHeader = dict()
    customHeader['User-Agent'] = Config.KOALA_USER_AGENT

    # 网络出错重试机制
    retryTimes = 0
    while True:
        try:
            # 先发送head做检测工作
            rsp = requests.head(url, headers=customHeader)
            if not rsp.ok:
                rsp.raise_for_status()
            if not rsp.headers['content-type'].startswith('text/html'):
                raise TypeError('Specified url do not return HTML file')

            rsp = requests.get(url, headers=customHeader)
            return to_unicode(rsp.content)
        except requests.exceptions.RequestException as error:
            write_stderr(repr(error))
            if retryTimes < Config.NETWORK_ERROR_MAX_RETRY_TIMES:
                retryTimes += 1
                time.sleep(Config.NETWORK_ERROR_WAIT_SECOND)
            else:
                raise

def is_two_url_same(url1, url2):
    '''
    比较两个url是否相同

    @param url1: 第一个url
    @type url1: 字符串
    @param url2: 第二个url
    @type url2: 字符串

    @return: 相同返回True，不同返回False
    @rtype: 布尔值
    '''
    pattern = re.compile(r'^[^:]+://', re.I | re.U)
    # 去除scheme前缀
    if pattern.search(url1):
        u1 = pattern.sub('', url1)
    else:
        u1 = url1
    if pattern.search(url2):
        u2 = pattern.sub('', url2)
    else:
        u2 = url2
    # 尾部保持/
    if not u1.endswith('/'):
        u1 += '/'
    if not u2.endswith('/'):
        u2 += '/'

    return u1 == u2


def ensure_url_default_scheme(url):
    '''
    确保没有http前缀的url地址以默认http前缀开头

    @param url: url地址
    @type url: 字符串

    @return: 处理后的url地址
    @rtype: 字符串
    '''
    # 检查url前缀，如果没有则添加默认前缀
    if not urlparse.urlsplit(url).scheme:
        return Config.URL_DEFAULT_SCHEME + url
    else:
        return url


def get_domain(url):
    '''
    从url地址里提取域名部分

    @param url: url地址
    @type url: 字符串

    @return: 域名部分
    @rtype: 字符串
    '''
    tldStruct = tldextract.extract(url)
    if tldStruct.tld:
        domain = tldStruct.domain + '.' + tldStruct.tld
    else:
        domain = tldStruct.domain

    return domain
