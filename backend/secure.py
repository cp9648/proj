# -*- coding: utf-8 -*-
'''
安全函数封装
'''
from functools import wraps

from flask import session, redirect, url_for

def login_required(func):
    '''登录限制-装饰器'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # 判断用户是否不存在于在session中
        not_in_s = not 'user' in session or session['user'] is None
        if not_in_s:
            # 如果用户不在session中，跳转到登录页面
            return redirect(url_for('view_login'))
        return func(*args, **kwargs)
    return decorated_function
