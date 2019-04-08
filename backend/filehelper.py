# -*- coding: utf-8 -*-
'''
文件帮助函数封装
'''
import os
import re
import mimetypes
import shutil
import traceback

from werkzeug.datastructures import FileStorage
from flask import send_file, Response, make_response, abort

from . import utils
from .database import User, File, UserFile, UserFolder, UserFileVersion


def file_partial(path, request, force=False):
    """ 
    文件获取
    from: http://blog.asgaard.co.uk/2012/08/03/http-206-partial-content-for-flask-python
    Simple wrapper around send_file which handles HTTP 206 Partial Content
    (byte ranges)
    TODO: handle all send_file args, mirror send_file's error handling
    (if it has any)
    """
    if not force:
        range_header = request.headers.get('Range', None)
    else:
        range_header = 'bytes=0-'
    if not range_header:
        return send_file(path)
    size = os.path.getsize(path)
    byte1, byte2 = 0, None
    
    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()
    if bool(g):
        if bool(g[0]):
            byte1 = int(g[0])
        if len(g) > 1 and bool(g[1]):
            byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1
    
    data = None
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True
    )
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(
        byte1,
        byte1 + length - 1,
        size
    ))

    return rv

def file_response(store_folder, path, request):
    '''请求文件响应'''
    store_file = os.path.join(store_folder, doc_path)
    if os.path.exists(store_file) and os.path.isfile(store_file):
        header_modify = request.headers.get('If-Modified-Since')
        modify_time = os.path.getmtime(store_file)
        if bool(modify_time) and isinstance(modify_time, float):
            file_modify = utils.fromTimeStamp(modify_time).ctime()
        else:
            file_modify = None
        if bool(header_modify) and header_modify == file_modify:
            return Response(status=304)
        mime = utils.getMimeType(store_file)
        if 'X-Nginx-Redirect' in request.headers:
            flag = request.headers['X-Nginx-Redirect']
            if flag == 'yes':
                resp = Response(
                    mimetype=mime
                )
                resp.headers['X-Accel-Redirect'] = doc_path
                return resp
        if bool(request.headers.get('Range', None)):
            return file_partial(store_file)
        size = os.path.getsize(store_file)
        if size > 1024 * 512:
            # 大于512kb时强制分片
            return file_partial(store_file, True)
        args = {
            'mimetype': mime
        }
        resp = make_response(send_file(store_file, **args))
        resp.headers.add('Accept-Ranges', 'bytes')
        if not file_modify is None:
            resp.headers['Last-Modified'] = file_modify
        return resp
    return abort(404)

class Uploader(object):
    '''文件上传处理类'''
    def __init__(self, db, cache_folder=None, store_folder=None):
        '''构造函数'''
        # 数据库
        self.db = db
        # 当前目录
        _cwd = os.getcwd()
        # 缓存目录
        self.cache_folder = cache_folder if bool(cache_folder) else os.path.join(_cwd, 'upload', 'cache')
        if cache_folder is None:
            utils.ensure_folder(self.cache_folder)
        # 存储目录
        self.store_folder = store_folder if bool(store_folder) else os.path.join(_cwd, 'upload' 'store')
        if store_folder is None:
            utils.ensure_folder(self.store_folder)

    def handle_file_request(self, user_id, request, file_field_key='file', path_key='path', uuid_key='uuid'):
        '''处理文件上传请求'''
        # 获取uuid
        req_uuid = request.values.get(uuid_key, None)
        if not bool(req_uuid):
            return (False, '缺少参数[{0}]'.format(uuid_key))
        # 读取上传目录
        user_folder_id = self.get_user_folder_id(user_id, request, path_key=path_key)
        if user_folder_id is None:
            return (False, '获取用户文件夹失败')
        # 读取上传的文件
        # 上传多个文件时，根据文件表单的name得到文件列表
        req_file_list = request.files.getlist(file_field_key)
        if len(req_file_list) > 1:
            # 从文件列表中取出文件，挨个保存
            for file in req_file_list:
                req_file_list.append(file)
        else:
            # 上传单个文件时，根据文件表单的name得到文件对象
            file = request.files.get(file_field_key, None)
            req_file_list.append(file)
        # 处理文件
        if bool(req_file_list):
            result = []
            for file_obj in req_file_list:
                item_ret = self.store_file(file_obj, user_folder_id, req_uuid)
                result.append(item_ret)
            return (True, 'TODO')
        else:
            return (False, '没有文件')

    def store_file(self, file_obj, user_folder_id, req_uuid):
        '''保存(缓存)文件'''
        cache_result = self.cache_file(file_obj, _uuid)
        if cache_result is None:
            return (1, '文件未找到', None)
        (can_save, is_saving, cache_file) = cache_result
        # 判断文件是否保存完成
        if can_save: # 保存完成
            # 获取文件信息
            file_name = file_obj.filename # 文件名
            file_ext = utils.get_file_ext(file_name) # 文件后缀名
            file_size = os.path.getsize(cache_file) # 文件大小
            # 获取mime信息
            file_mime = utils.getMimeType(file_name)
            (mime_major, mime_minor) = (None, None)
            if bool(file_mime):
                (mime_major, mime_minor) = file_mime.split('/')
            # 计算md5
            file_md5 = utils.file_md5sum(cache_file)
            # 构造存储文件名（md5 _-_ 文件名）
            # save_name = '{0}_-_{1}'.format(file_md5, file_name) # 未采用的文件名构造
            save_name = '{0}.{1}'.format(file_md5, file_ext)
            # 完整存储文件
            save_target = os.path.join(self.store_folder, save_name)
            db_ok = self.db_save_file(user_folder_id, file_name, file_md5, mime_major, mime_minor, file_size, save_name)
            if db_ok:
                # 存储文件到物理存储目录
                shutil.move(cache_file, save_target)
                # 如果文件存在了，说明保存成功了
                if os.path.exists(save_target) and os.path.isfile(save_target):
                    self.db.session.commit()
                    return (0, '文件上传完成', file_name)
                else:
                    self.db.session.rollback()
                    return (4, '文件保存失败', file_name)
            else:
                self.db.session.rollback()
                os.remove(cache_file)
                return (3, '数据保存失败', file_name)
        else:
            if is_saving: # 分片保存完成
                return (0, '文件上传中', file_name)
            else:
                return (2, '文件上传失败', file_name)

    def cache_file(self, file_obj, _uuid):
        '''缓存文件'''
        if not isinstance(file_obj, FileStorage):
            return None
        cache_file = os.path.join(self.cache_folder, _uuid + '@' + file_obj.filename)
        _size = 0
        _range = {}
        _ext = utils.get_file_ext(cache_file)
        can_save = False
        if 'Content-Range' in request.headers:
            # 获取分块头
            range_str = request.headers['Content-Range']
            # 解析分块大小
            range_pattern = r'bytes (\d+)-(\d+)/(\d+)'
            mat = re.match(range_pattern, range_str)
            if mat:
                _range['begin'] = int(mat.group(1))
                _range['end'] = int(mat.group(2))
                _range['sum'] = int(mat.group(3))
                # 保存文件分片，追加方式
                with open(cache_file, 'ab') as f:
                    f.seek(_range['begin'])
                    f.write(value.stream.read())
            else:
                value.save(cache_file)
                can_save = True
        else:
            # 不是分片上传时，直接存储整个文件
            # http://docs.jinkan.org/docs/flask/patterns/fileuploads.html#uploading-files
            value.save(cache_file)
            can_save = True
        is_saving = False
        if os.path.exists(cache_file):
            _size = os.path.getsize(cache_file)
            if not can_save:
                if abs(_size - _range['sum']) < 1:
                    can_save = True
                else:
                    is_saving = True
        else:
            can_save = False
        
        return (can_save, is_saving, cache_file)

    def db_save_file(self, user_id, user_folder_id, file_name, file_md5, mime_major, mime_minor, file_size, save_name):
        '''添加数据库记录'''
        try:
            # 保存文件到数据库
            ## 文件记录
            file_obj = File(file_md5, mime_major, mime_minor, file_size, save_name)
            self.db.session.add(file_obj)
            self.db.session.flush()
            file_id = file_obj._id

            ## 用户文件记录
            # 先查询是否已经存在
            uf_obj = UserFile.query.filter_by(
                filename=file_name,
                user_id=user_id,
                folder_id=user_folder_id
            ).first()
            if not isinstance(uf, UserFile):
                # 如果未查到，说明是新文件，则添加
                uf_obj = UserFile(file_name, user_id, user_folder_id)
                self.db.session.add(uf_obj)
                self.db.session.flush()
                uf_id = uf_obj._id
            else:
                uf_id = uf._id

            ## 用户文件版本
            # 先查询是否已经存在
            uf_query = UserFileVersion.query.filter_by(
                user_file_id=uf_id,
                file_id=file_id
            )
            ufv_obj = UserFileVersion(uf_id, file_id)
            # 注：如果未查到，说明是是新用户文件，则添加的第一个版本(默认版本为1，不用处理)
            if uf_query.count() > 0:
                # 如果存在旧版本，则先查询最大版本号，并添加新的版本
                ufv_max_obj = uf_query.order_by(UserFileVersion.version.desc()).first()
                new_version = ufv_max_obj.version + 1
                # 指定新版本
                ufv_obj.version = new_version
            self.db.session.add(ufv_obj)
            self.db.session.flush()
            ufv_id = ufv_obj._id
            pass
        except:
            return False
        else:
            return True
    
    def get_user_folder_id(self, user_id, request, path_key='path'):
        '''获取用户文件夹id'''
        # 获取请求路径（文件夹）
        req_path = request.values.get(path_key, None)
        if not bool(req_path) or req_path == '/':
            req_path = None
        # 获取用户文件夹ID
        user_folder_id = None
        if bool(req_path):
            uf = UserFolder.query
            uf = UserFolder.query.filter_by(
            user_id=user_id,
            path=req_path
        ).first()
        if isinstance(uf, UserFolder):
            user_folder_id = uf._id.filter_by(
                user_id=user_id,
                path=req_path
            ).first()
            if isinstance(uf, UserFolder):
                user_folder_id = uf._id
        # 如果根据上传的目录 找不到，就上传到根目录（path为None）
        if user_folder_id is None:
            uf = UserFolder.query
            uf = UserFolder.query.filter_by(
            user_id=user_id,
            path=req_path
        ).first()
        if isinstance(uf, UserFolder):
            user_folder_id = uf._id.filter_byfilter_by(
                user_id=user_id,
                path=None
            ).first()
            if not isinstance(uf, UserFolder):
                return None
            user_folder_id = uf._id
        return user_folder_id
