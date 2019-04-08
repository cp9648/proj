# -*- coding: utf-8 -*-
'''
工具函数封装
'''
import os
import hashlib
import mimetypes

import pytz


def io_md5sum(io_obj):
    '''计算io对象（比如：打开的文件）的md5值'''
    # 获取io对象指针位置
    origin_tell = io_obj.tell()
    # 将io对象指针移动到0
    io_obj.seek(0)
    # 得到md5算法对象
    hash_md5 = hashlib.md5()
    # 文件分块读取
    chunk_size = 4096 # 4096 字节（4KB）
    # 获取分块数据（bytes），一次读取 chunk_size 个字节
    chunk = io_obj.read(chunk_size)
    # 如果能读取到内容，就一直读取
    while bool(chunk):
        # 应用MD5算法，计算
        hash_md5.update(chunk)
        # 继续读
        chunk = io_obj.read(chunk_size)
    # 恢复io对象指针位置
    io_obj.seek(origin_tell)
    # 返回计算结果(16进制字符串，32位字符)
    return hash_md5.hexdigest()

def file_md5sum(file_path):
    '''计算文件md5值'''
    result = None
    # 以二进制方式读文件
    with open(file_path, "rb") as f:
        result = io_md5sum(f)
    return result

def calc_md5(msg):
    '''计算md5'''
    hash_md5 = hashlib.md5()
    if isinstance(msg, str):
        # 准备要计算md5的数据（bytes类型）
        msg = msg.encode('utf-8', errors='ignore')
    # 计算md5
    hash_md5.update(msg)
    # 计算结果(16进制字符串，32位字符)
    return hash_md5.hexdigest()

def get_file_ext(file_path):
    '''获取文件扩展名'''
    arr = os.path.splitext(file_path)
    return arr[-1] if len(arr) > 1 else None

def getMimeType(file_name):
    '''获取文件MIMEType'''
    mimetypes.init()
    file_ext = get_file_ext(file_name)
    return mimetypes.types_map.get(file_ext, None) if bool(file_ext) else None

def fromTimeStamp(timestamp, tz=None):
    '''从时间戳得到datetiem对象'''
    if tz is None:
        tz = pytz.timezone('Asia/Shanghai')
    return datetime.fromtimestamp(timestamp, tz)

def ensure_folder(folder_path):
    '''确保目录存在'''
    # 如果目录不存在
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        # 创建目录
        os.makedirs(folder_path)