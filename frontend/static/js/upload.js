/**
 * 检查上传列表
 */
function check_next_upload(data) {
    var upload_quene = $(document.body).data('upload-quene');
    if(upload_quene.length > 0) {
        upload_quene.shift();
        if(upload_quene.length > 0) {
            var next_upload = upload_quene[0];
            $(document.body).data('upload-quene', upload_quene);
            $(document.body).attr('upload-progress-id', next_upload['id']);
            data.context = $('#' + next_upload['id']).find('.update-status');
            var xhr = next_upload.submit();
            data.context.data('data', {jqXHR: xhr});
        }
    }
    else {
        $(document.body).removeAttr('upload-progress-id');
    }
}

/**
 * 添加文件时调用
 */
function on_file_add(event, data) {
    var _current_id = 'id_' + generateUUID().replace(/\-/g, '_');
    var filename = data.files[0].name,
        filesize = formatFileSize(data.files[0].size);
    var _progress = [
        '<li class="list-group-item" id="', _current_id,'">',
            '<div style="height: 1em;">',
                '<span class="current-update-name">', filename, '</span>',
                '<span class="update-size text-muted">(', filesize, ')</span>',
                '<span class="update-status">等待中</span>',
            '</div>',
            '<div class="progress">',
                '<div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em;">0%</div>',
            '</div>',
        '</li>'
    ].join('');
    $('#upload-list').append(_progress);
    var upload_quene = $(document.body).data('upload-quene');
    if(!upload_quene) {
        upload_quene = [];
        $(document.body).data('upload-quene', upload_quene);
    }
    // 记忆唯一ID
    data['id'] = _current_id;
    // 记忆上传路径
    // 从cookies中获取path
    var _path = $.AMUI.utils.cookie.get('current_path');
    // 处理path，确保数据有效性
    if(_path == '/' || _path === undefined || _path === null || _path == '') {
        // 忽略data
    }
    else {
        data['upload_path'] = _path;
    }
    // 文件夹
    var relative_path = data.files[0].webkitRelativePath;
    if(!!relative_path && relative_path.length > 0) {
        var idx = relative_path.lastIndexOf('/');
        var folder = relative_path.substr(0, idx);
        if(folder.length > 0) {
            data['relative_folder'] = folder;
        }
    }
    // 绑定状态上下文
    data.context = $('#' + _current_id).find('.update-status');
    // 添加到上传队列
    upload_quene.push(data);
    if(upload_quene.length < 2) {
        $(document.body).attr('upload-progress-id', _current_id);
        var xhr = data.submit();
        data.context.data('data', {jqXHR: xhr});
    }
}

/**
 * 上传失败时调用
 */
function on_upload_failed($self, event, data) {
    var fu = $self.data('blueimp-fileupload') || $self.data('fileupload');
    var retries = 0;
    try {
        retries = data.context.data('retries') || 0;
    }
    catch (ex) {
        retries = 0;
    }
    var retry = function () {
        var _file_name = data.id + '@' + data.files[0].name;
        $.getJSON(
            GLOBAL.RESUME_UPLOAD_URL, {file: _file_name}
        ).done(function (result) {
            var file = result.file;
            data.uploadedBytes = file && file.size;
            // clear the previous data:
            data.data = null;
            data.submit();
        }).fail(function () {
            fu._trigger('fail', event, data);
        });
    };
    if (data.errorThrown !== 'abort' &&
            data.uploadedBytes < data.files[0].size &&
            retries < fu.options.maxRetries) {
        retries += 1;
        data.context.data('retries', retries);
        window.setTimeout(retry, retries * fu.options.retryTimeout);
        return;
    }
    if(data.context) {
        data.context.removeData('retries');
    }
    var fail_func = $.blueimp.fileupload.prototype.options.fail;
    if(fail_func) {
        fail_func.call($self[0], event, data);
    }
}

/**
 * 绑定文件上传按钮操作
 */
function bind_file_upload() {
    // 屏蔽页面默认拖拽事件
    $(document).on('drop dragover', function(event) {
        event = evnet || window.event;
        event.preventDefault();
    });

    // 初始化上传组件
    var $file_elem = $('.button-line').find('input[name="file"]');
    $('.button-line').fileupload({
        url: GLOBAL.UPLOAD_URL,
        fileInput: $file_elem, // 文件表单
        dropZone: $(document.body),
        paramName: 'file',
        replaceFileInput: true, // 文件表单更新替换
        dragdrop: true,
        dataType: 'json',
        singleFileUploads: true,
        limitMultiFileUploads: 1,
        limitConcurrentUploads: 1,
        autoUpload: true,
        sequentialUploads: true,
        maxRetries: 100,
        retryTimeout: 500,
        maxChunkSize: 1024 * 1024 * 10, // 10 MB
        formData: function(form) { // 文件之外的表单数据
            var data = form.serializeArray();
            // 参考： https://github.com/blueimp/jQuery-File-Upload/wiki/Options#formdata
            if(!!this.upload_path) {
                data.push({
                    'name': 'path',
                    'value' : this.upload_path
                });
            }
            if(!!this.relative_folder) {
                data.push({
                    'name': 'relative',
                    'value' : this.relative_folder
                });
            }
            data.push({
                name: 'uuid',
                value: this.id
            });
            return data;
        },
        add: function (event, data) {
            on_file_add(event, data);
        },
        submit: function(event, data) {
            // console.log(data);
        },
        send: function(event, data) {
            // console.log(data);
        },
        progressall: function(event, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            console.log(progress);
            var $current_li = $(['#', $(document.body).attr('upload-progress-id')].join(''));
            var $progress_bar = $current_li.find('.progress-bar');
            $progress_bar.css('width', progress + '%');
            $progress_bar.text(progress + '%');
            $progress_bar.attr('aria-valuenow', progress);
            $current_li.find('.update-status').text('上传中');
        },
        done: function(event, data) { // 文件上传完成之后调用
            // 取得服务器返回的结果
            var result = data.result;
            console.log(result)

            var $current_li = $(['#', $(document.body).attr('upload-progress-id')].join(''));
            $current_li.find('.update-status').text('已上传');
            setTimeout(function() {
                $current_li.find('.progress').fadeOut(1000);
                check_next_upload(data);
            }, 300);
        },
        fail: function(event, data) {
            var $self = $(this);
            on_upload_failed($self, event, data);
        }
    });
}

/**
 * 绑定上传面板折叠事件
 */
function bind_upload_panel() {
    var $ico = $('#modal-upload-title [class*=am-icon-angle-]');
    $ico.on('click', function() {
        var $self = $(this);
        var $modal = $('#bottom-right-modal');
        var $bd = $modal.find('.am-modal-dialog .am-modal-bd');
        if($self.hasClass('am-icon-angle-down')) {
            $self.removeClass('am-icon-angle-down');
            $self.addClass('am-icon-angle-right');
            $bd.hide(300, function() {
                if(!$modal.hasClass('panel-min-width')) {
                    $modal.addClass('panel-min-width');
                }
            });
        }
        else if($self.hasClass('am-icon-angle-right')) {
            $self.removeClass('am-icon-angle-right');
            $self.addClass('am-icon-angle-down');
            $bd.show(100, function() {
                if($modal.hasClass('panel-min-width')) {
                    $modal.removeClass('panel-min-width');
                }
            });
        }
    });
}