# -*- coding:utf-8 -*-

'''
Created on 2013-4-26
@author: niexinxin
'''
from __future__ import print_function
import sys
import traceback
from bs4 import UnicodeDammit
from model.video_info import Video_Info


def write_stdout(format, *args):
    '''
    写log到标准输出
    @return: 无
    '''
    try:
        format = format_str(format, *args)
        print(format, file=sys.stdout)
    except UnicodeEncodeError:
        print("Error happened on Log.write_stdout", file=sys.stderr)
        print('---->exception: ', file=sys.stderr)
        traceback.print_exc()
        print('---->stack:', file=sys.stderr)
        traceback.print_stack()

def write_stderr(format, *args):
    '''
    写log到标准错误输出
    @return: 无
    '''
    try:
        format = format_str(format, *args)
        print(format, file=sys.stderr)
    except UnicodeEncodeError:
        print("Error happened on Log.write_stderr", file=sys.stderr)
        print('---->exception: ', file=sys.stderr)
        traceback.print_exc()
        print('---->stack:', file=sys.stderr)
        traceback.print_stack()


def format_str(format, *args):
    if format == None:
        write_stderr('parameter format is None')
        return ''

    if not isinstance(format, str):
        format = '%s' % format

    format = to_unicode(format)
    args_list = list()
    for v in list(args):
        v = to_unicode(v)
        args_list.append(v)

    args = tuple(args_list)
    if args:
        format = format % args

    return format


def to_unicode(obj):
    #print(type(obj))
    if isinstance(obj, (int, long, float, unicode)):
        return obj

    elif isinstance(obj, str):
        return __to_unicode_for_str(obj)

    elif isinstance(obj, tuple):
        return __to_unicode_for_tuple(obj)

    elif isinstance(obj, list):
        return __to_unicode_for_list(obj)

    elif isinstance(obj, dict):
        return __to_unicode_for_dict(obj)

    else:
        return __to_unicode_for_others(obj)


def __to_unicode_for_str(str_obj):
    if isinstance(str_obj, unicode):
        return str_obj
    else:
        dammit = UnicodeDammit(str_obj)
        return dammit.unicode_markup


def __to_unicode_for_tuple(tuple_obj):
    uincode_list = list()
    for v in list(tuple_obj):
        v = to_unicode(v)
        uincode_list.append(v)

    return tuple(uincode_list)


def __to_unicode_for_list(list_obj):
    uincode_list = list()
    for v in list_obj:
        v = to_unicode(v)
        uincode_list.append(v)

    return uincode_list


def __to_unicode_for_dict(dict_obj):
    unicode_dic = dict()
    for key in dict_obj.keys():
        u_key = to_unicode(key)
        u_value = to_unicode(dict_obj[key])
        unicode_dic[u_key] = u_value

    return unicode_dic


def __to_unicode_for_others(other_obj):
    #print('__to_unicode_for_others.obj.type = ', type(other_obj))
    base_str = '%s' % other_obj
    return  to_unicode(base_str)


def test():
    write_stdout('a=%d, b=%.2f, c=%s', 1, 2.0, 'hello world')
    write_stdout('影片名称: %s, %d', u'痞子厨子戏子2013', 12)
    write_stdout(u'上映时间: %s', "2013年")
    video_info = Video_Info()
    video_info.title = '痞子厨子戏子2013'
    video_info.area = '内地'
    video_info.public_time = '2013'
    video_info.qhash_list = ['qvod://kdajfkldj/痞子厨子戏子.rmvb', 'qvod://kdajfkldj/痞子厨子戏子.dvd']
    write_stdout('%d, %f, %s, %s', 1, 2.0, u'视频信息', video_info)
    write_stderr("test finished!")

    gbkstr = u'痞子厨子戏子'.encode('gbk', 'ignore')
    write_stdout('gbk test %s', gbkstr)

if __name__ == "__main__":
    test()

