# -*- coding: utf-8 -*-
'''
配置
'''
import os


# 数据库连接字符串（# 读取区环境变量PROJ_ROOT）
DB_URI = 'sqlite:///{0}'.format(
    os.path.join(os.environ['PROJ_ROOT'], 'data.db3')
)
# 数据存储目录
STORE_PATH = os.path.join(os.environ['PROJ_ROOT'], 'upload', 'store')
# 上传缓存目录
UPLOAD_CACHE_PATH = os.path.join(os.environ['PROJ_ROOT'], 'upload', 'cache')
# session密钥
SECRET_KEY = 'hello file cloud'
# 运行配置
RUN_CFG = {
    'host': '127.0.0.1',
    'port': 5000,
    'debug': True
}