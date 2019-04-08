# -*- coding: utf-8 -*-
'''
web应用-启动文件
'''
import os
# 设置环境变量PROJ_ROOT
os.environ['PROJ_ROOT'] = os.getcwd()


from backend.main import start_server


if __name__ == '__main__':
    start_server()