# -*- coding: utf-8 -*-
'''
后端主入口
'''
import os

from . import app
from .database import db, config
from . import views, utils
from .filehelper import Uploader


app.config['SECRET_KEY'] = config.SECRET_KEY

def start_server():
    '''启动web服务'''
    # 配置调试模式
    is_debug = config.RUN_CFG.get('debug', False)
    if is_debug:
        app.debug = True
        # 添加调试工具条
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        # from flask_debugtoolbar import DebugToolbarExtension
        # toolbar = DebugToolbarExtension(app)
    # 如果数据库不存在就创建
    db.create_all()
    # 确保数据存储目录存在
    utils.ensure_folder(config.STORE_PATH)
    # 确保上传缓存目录存在
    utils.ensure_folder(config.UPLOAD_CACHE_PATH)
    # 将上传工具类附加到app上
    app.uploader = Uploader(db, cache_folder=config.UPLOAD_CACHE_PATH, store_folder=config.STORE_PATH)
    # 运行web服务器
    app.run(**config.RUN_CFG)