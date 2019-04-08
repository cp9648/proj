# -*- coding: utf-8 -*-
'''
web视图
'''
import json
import os

from flask import (
    session, redirect, url_for, request, flash,
    render_template, render_template_string, current_app
)
from sqlalchemy.sql import and_ as sql_and

from . import app
from .secure import login_required
from .database import db, User, UserFolder
from . import utils, config


@app.route('/empty')
@login_required
def view_empty():
    '''视图-(空)首页'''
    tmpl_str = '''这里是首页 <br /> <a href="{{ url_for('view_logout') }}">注 销</a>'''
    return render_template_string(tmpl_str)

@app.route(r'/login', methods=['GET', 'POST'])
def view_login():
    '''视图-登录'''
    in_s = 'user' in session and session['user'] is not None
    if in_s:
        # 如果已经登录了，跳转到首页
        return redirect(url_for('view_index'))
    # 如果是POST请求，才判断是否是要登录
    if request.method == 'POST':
        # 获取请求参数
        req_username = request.values.get('username', None)
        req_password = request.values.get('password', None)
        # 参数检测
        if req_username is not None and req_password is not None:
            # 去掉首尾的空白字符
            _username = req_username.strip()
            _password = req_password.strip()
            if bool(_username):
                if not bool(_password):
                    flash('缺少密码')
                else:
                    # 查询用户信息
                    cursor = User.query.filter(sql_and(
                        User.username == _username,
                        User.password == utils.calc_md5(_password)
                    ))
                    # 判断查询结果条数
                    if cursor.count() > 0:
                        # 取得第一条数据
                        user_obj = cursor.first()
                        # 设置session（注意：session值不能使User对象，需要是Python内置类型）
                        session['user'] = user_obj.to_dict()
                        # 跳转
                        return redirect(url_for('view_index'))
                    else:
                        flash('用户名或密码错误')
            else:
                flash('缺少用户名')
        else:
            flash('缺少参数')
    return render_template('login.html')

@app.route(r'/logout', methods=['GET'])
@login_required
def view_logout():
    '''视图-注销'''
    # 移除session
    session.pop('user', None)
    # 跳转到登录页面
    return redirect(url_for('view_login'))

@app.route(r'/', methods=['GET'])
@login_required
def view_index():
    return render_template('index.html')

@app.route(r'/ajax-user-folder-list', methods=['GET', 'POST'])
@login_required
def view_user_folder_list():
    # 从session中取得用户
    s_user = session['user']
    # 获取请求路径
    req_path = request.values.get('path', None)
    if not bool(req_path) or req_path == '/':
        req_path = None
    # 查询文件夹列表（UserFolder对象列表）
    uf_list = UserFolder.list_by_path(s_user['_id'], req_path)
    # 讲UserFolder转为Python内置数据类型(dict)
    uf_list = list(map(lambda item: item.to_dict(), uf_list))
    # 讲文件夹列表转为json格式的字符串
    return json.dumps(uf_list, ensure_ascii=False)

@app.route(r'/resume-upload', methods=['GET', 'POST'])
@login_required
def view_resume_upload(_suffix=None):
    '''断点续传'''
    # 获取文件
    file_name = request.values.get('file')
    # 读取配置
    store_folder = config.STORE_PATH
    cache_folder = config.UPLOAD_CACHE_PATH
    # 缓存文件目录
    cache_file = os.path.join(cache_folder, file_name)
    # 获取已经保存了的文件大小
    if os.path.exists(cache_file):
        _size = os.path.getsize(cache_file)
    else:
        _size = 0
    ret = {
        'file': {
            'size': _size
        }
    }
    return json.dumps(ret, ensure_ascii=False)

@app.route('/upload', methods=['POST'])
@login_required
def view_upload():
    '''文件上传'''
    kwargs = {
        'file_field_key': 'file',
        'path_key': 'path',
        'uuid_key': 'uuid'
    }
    try:
        user_id = session['user']['_id']
        upload_result = current_app.uploader.handle_file_request(self, user_id, request, **kwargs)
    except:
        ex_msg = traceback.format_exc()
        # TODO save to log
        upload_result = None
    if not upload_result is None:
        return json.dumps({
            'error': 0,
            'desc': 'TODO ...',
            'files': upload_result
        })
    else:
        return json.dumps({
            'error': 10,
            'desc': '服务器错误'
        })