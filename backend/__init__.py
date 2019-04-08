# -*- coding: utf-8 -*-
import os
if 'PROJ_ROOT' not in os.environ:
    # 如果没有设置环境变量PROJ_ROOT，防止出错
    os.environ['PROJ_ROOT'] = os.path.dirname(os.path.dirname(__file__))

from flask import Flask


app = Flask(
    __name__,
    static_folder=os.path.join(os.environ['PROJ_ROOT'], 'frontend', 'static'),
    template_folder=os.path.join(os.environ['PROJ_ROOT'], 'frontend', 'templates'),
    instance_relative_config=True
)