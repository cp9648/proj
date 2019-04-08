# -*- coding: utf-8 -*-
'''
开发阶段-初始化数据
'''
import os
# 设置环境变量PROJ_ROOT
os.environ['PROJ_ROOT'] = os.getcwd()

from backend.utils import calc_md5
from backend.database import db, User, UserFolder


def init_user():
    '''初始化用户（确保至少有一个[原始]用户）'''
    cursor = User.query
    if cursor.count() < 1:
        usr = User(username='admin', password=calc_md5('123456'))
        db.session.add(usr)
        db.session.commit()
        print(usr.to_dict())
    else:
        print('用户已存在:')
        print(cursor.first().to_dict())

def add_folder():
    u = User.query.first()
    uf = UserFolder(None, u._id)
    db.session.add(uf)
    db.session.add(UserFolder('/home', u._id))
    db.session.add(UserFolder('/home/zhangsan', u._id))
    db.session.add(UserFolder('/home/lisi', u._id))
    db.session.add(UserFolder('/home/lisi/python', u._id))
    db.session.add(UserFolder('/home/lisi/3', u._id))
    db.session.add(UserFolder('/home/lisi/2', u._id))
    db.session.add(UserFolder('/home/lisi/java', u._id))
    db.session.add(UserFolder('/root', u._id))
    db.session.commit()
    print(uf)


if __name__ == '__main__':
    # 确保数据库存在
    db.create_all()
    # 添加初始用户
    init_user()
    # 添加初始文件夹
    add_folder()