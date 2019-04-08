# -*- coding: utf-8 -*-
'''
数据库
'''
import re
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func

from . import app
from . import config


app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    """用户-模型类"""
    __tablename__ = 'user'
    
    _id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='ID')
    username = db.Column(db.String(20), nullable=False, unique=True, comment='用户名')
    password = db.Column(db.String(32), nullable=False, comment='密码')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<{0} {1}>'.format(__class__.__name__, repr(self.username))

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'password': self.password
        }

class File(db.Model):
    """文件-模型类"""
    __tablename__ = 'file'

    _id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='ID')
    md5 = db.Column(db.String(32), nullable=False, unique=True, comment='文件MD5')
    mime_major = db.Column(db.String(16), nullable=True, comment='MIME主类型')
    mime_minor   = db.Column(db.String(16), nullable=True, comment='MIME次类型')
    file_size = db.Column(db.Integer, nullable=False, comment='文件大小(字节)')
    store_path = db.Column(db.String(255), nullable=False, unique=True, comment='文件相对存储路径')
    ref_count = db.Column(db.Integer, nullable=False, default=1, comment='引用计数次数')

    def __init__(self, md5, mime_major, mime_minor, file_size, store_path, ref_count=None):
        self.md5 = md5
        self.mime_major = mime_major
        self.mime_minor = mime_minor
        self.file_size = file_size
        self.store_path = store_path
        if ref_count is not None:
            self.ref_count = ref_count

    def __repr__(self):
        return '<{0} {1}>'.format(__class__.__name__, repr(self.store_path))

class UserFolder(db.Model):
    """用户文件夹-模型类"""
    __tablename__ = 'user_folder'

    _id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='ID')
    path = db.Column(db.String(255), nullable=True, comment='文件夹路径')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户id')
    update_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now, comment='更新时间')
    __table_args__ = (
        db.UniqueConstraint('path', 'user_id', name='uix_path_user_id'),
    )

    def __init__(self, path, user_id, update_time=None):
        self.path = path
        self.user_id = user_id
        if update_time is not None:
            self.update_time = update_time

    def __repr__(self):
        return '<{0} {1}>'.format(__class__.__name__, repr(self.path))

    @classmethod
    def list_by_id(cls, user_id, folder_id, reverse=False):
        '''根据文件夹id获取子目录'''
        uf = cls.query.filter_by(_id=folder_id, user_id=user_id).first()
        return cls.list_by_path(user_id, uf.path, reverse=reverse) if isinstance(uf, cls) else []

    @classmethod
    def list_by_path(cls, user_id, folder_path=None, reverse=False):
        '''根据文件夹路径获取子目录'''
        if folder_path is None:
            folder_path = ''
        # 去掉结尾的/
        if folder_path.endswith('/'):
            folder_path = folder_path[:-1]
        pattern = r'^{0}/[^/]+$'.format(folder_path)
        # 排序函数（根据什么属性来排序）
        sort_func = lambda item: item.path
        return sorted([
            uf for uf in cls.query.filter(and_(
                cls.path != None,
                cls.user_id == user_id
            ))
            if re.match(pattern, uf.path, re.I)
        ], key=sort_func, reverse=reverse)

    def to_dict(self):
        return {
            '_id': self._id,
            'path': self.path,
            'user_id': self.user_id,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class UserFile(db.Model):
    """用户文件-模型类"""
    __tablename__ = 'user_file'

    _id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='ID')
    filename = db.Column(db.String(255), nullable=False, comment='文件名')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='用户id')
    folder_id = db.Column(db.Integer, db.ForeignKey('user_folder.id'), nullable=True, comment='文件夹id')
    update_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now, comment='更新时间')
    # https://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns
    __table_args__ = (
        db.UniqueConstraint('filename', 'user_id', 'folder_id', name='uix_filename_user_id_folder_id'),
    )

    def __init__(self, filename, user_id, folder_id, update_time=None):
        self.filename = filename
        self.user_id = user_id
        self.folder_id = folder_id
        if update_time is not None:
            self.update_time = update_time

    def __repr__(self):
        return '<{0} {1}>'.format(__class__.__name__, repr(self.filename))

class UserFileVersion(db.Model):
    """用户文件版本-模型类"""
    __tablename__ = 'user_file_version'

    _id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='ID')
    user_file_id = db.Column(db.Integer, db.ForeignKey('user_file.id'), nullable=False, comment='用户文件id')
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False, comment='文件id')
    version = db.Column(db.Integer, nullable=False, default=1, comment='版本号')
    store_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now, comment='存储时间')

    def __init__(self, user_file_id, file_id, version=None, store_time=None):
        self.user_file_id = user_file_id
        self.file_id = file_id
        self.version = version
        if version is not None:
            self.version = version
        if store_time is not None:
            self.store_time = store_time

    def __repr__(self):
        return '<{0} ID={1},V={2}>'.format(__class__.__name__, self.user_file_id, self.version)