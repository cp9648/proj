/**
 * 生成唯一id
 * @see https://stackoverflow.com/a/8809472/6528523
 */
function generateUUID() {
    var d = new Date().getTime();
    if (typeof performance !== 'undefined' && typeof performance.now === 'function'){
        d += performance.now(); //use high-precision timer if available
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

/**
 * 格式化文件大小
 * @param _size 化文件大小(单位: 字节)
 */
function formatFileSize(_size) {
    _size = Number(_size);
    var _type= 'Byte'
    if(_size < 1024) {
        _type = '字节';
    }
    else if(_size < 1024 * 1024) {
        _size = (_size / 1024);
        _type = 'KB';
    }
    else if(_size < 1024 * 1024 * 1024) {
        _size = (_size / 1024 / 1024);
        _type = 'MB';
    }
    else if(_size < 1024 * 1024 * 1024 * 1024) {
        _size = (_size / 1024 / 1024 / 1024);
        _type = 'GB';
    }
    _size = _size.toFixed(3).toString().replace(/[\.]?0+$/, '')
    return _size + _type;
}

/**
 * 渲染目录列表
 */
function render_folder_list(data) {
    var $table = $('#user-folder-list');
    var $tbody = $table.find('tbody');
    // 清空现有数据
    $tbody.empty();
    if(!!data && data.length > 0) {
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            var path_index = item['path'].lastIndexOf('/');
            var path_name = item['path'].substr(path_index + 1);
            var tr_str = [
                '<tr>',
                    '<td>',
                        '<input type="checkbox" name="ckb-content">',
                    '</td>',
                    '<td>',
                        '<a href="javascript:;" data-path="', item['path'], '">', path_name, '</a>',
                    '</td>',
                    '<td>', item['update_time'], '</td>',
                    '<td>',
                        '<a href="javascript:;">重命名</a>',
                    '</td>',
                '</tr>'
            ].join('');
            $tbody.append(tr_str);
        }
    }
    else {
        // 没有数据时，给出提示
        var $thead = $table.find('thead');
        var col_count = $thead.find('th').length;
        $tbody.html([
            '<tr>',
                '<td colspan="', col_count, '">',
                    '<div class="am-text-center am-link-muted">穷得连个文件夹都没剩不下</div>',
                '</td>',
            '</tr>'
        ].join(''));
    }
}

/**
 * 渲染当前路径
 */
function render_current_path(path) {
    // 面包屑导航
    var $breadcrumb = $('.path-line > .am-breadcrumb');
    // 清空现有导航
    $breadcrumb.empty();
    // 目录分级数组
    var path_arr = [];
    // 当前处于主目录
    if(path == '/' || path === undefined || path === null || path == '') {
        path = '';
        path_arr.push(path);
    }
    else {
        // 目录分解
        path.replace(/\//g, function(mat) {
            var sub_path = arguments[2].substr(0, arguments[1]);
            path_arr.push(sub_path);
            return mat;
        });
        path_arr.push(path);
    }
    // 显示到界面上
    for (var i = 0; i < path_arr.length; i++) {
        var li = [];
        // 渲染主目录
        if(i == 0) {
            // 只有主目录
            if(path_arr.length == 1) {
                li = [
                    '<li>',
                        '<i class="am-icon-home"></i>主目录',
                    '</li>'
                ];
            }
            else {
                // 不只有主目录
                li = [
                    '<li>',
                        '<a href="javascript:;">',
                            '<i class="am-icon-home"></i>主目录',
                        '</a>',
                    '</li>'
                ];
            }
        }
        else {
            var path_index = path_arr[i].lastIndexOf('/');
            var path_name = path_arr[i].substr(path_index + 1);
            if(i == path_arr.length - 1) {
                li = [
                    '<li class="am-active">',
                        path_name,
                    '</li>'
                ];
            }
            else {
                li = [
                    '<li>',
                        '<a href="javascript:;">',
                            path_name,
                        '</a>',
                    '</li>'
                ];
            }
        }
        // 把构造的html源码添加到页面上
        var $li = $(li.join(''));
        if(path_arr[i] == '') {
            path_arr[i] = '/';
        }
        // 额外添加一个属性，用于记录目录跳转目标路径
        $li.attr('data-path', path_arr[i]);
        $breadcrumb.append($li);
    }
}

/**
 * 设置当前路径记录
 */
function set_current_path(path) {
    // 处理path，确保数据有效性
    if(path == '/' || path === undefined || path === null || path == '') {
        // 对于无意义的path，清除记录
        $.AMUI.utils.cookie.unset('current_path');
    }
    else {
        // 设置path
        $.AMUI.utils.cookie.set('current_path', path);
    }
}

/**
 * 获取目录列表
 */
function get_folder_list(path) {
    var _data = {};
    // 当path参数未提供时，获取当前路径
    if(!path) {
        // 从cookies中获取path
        path = $.AMUI.utils.cookie.get('current_path');
    }
    // 处理path，确保数据有效性
    if(path == '/' || path === undefined || path === null || path == '') {
        // 忽略data
    }
    else {
        _data['path'] = path;
    }
    // 发起ajax请求
    $.ajax({
        url: GLOBAL.USER_FOLDER_LIST_URL,
        data: _data,
        dataType: 'json',
        success: function(data) {
            // 当请求成功时，设置当前路径为请求的路径
            set_current_path(path);
            // 渲染路径
            render_current_path(path);
            // 显示数据
            render_folder_list(data);
        }
    });
}

/**
 * 绑定click事件，处理目录切换
 */
function bind_path_change() {
    // 元素获取
    var $breadcrumb = $('.path-line > .am-breadcrumb');
    var $tbody = $('#user-folder-list').find('tbody');
    // 公共click事件
    function a_click(event) {
        // event = event || window.event;
        // 得到当前点击的元素
        var $me = $(this);
        // 取得当前元素的data-path属性
        var path = $me.attr('data-path');
        // 如果当前元素是li
        if($me.is('li')) {
            // 如果当前元素的子元素中没有a，就return
            if($me.find('a').length < 1) {
                return;
            }
        }
        get_folder_list(path);
    }
    // 面包屑事件绑定
    $breadcrumb.on('click', 'li[data-path]', a_click);
    // 表格tbody事件绑定
    $tbody.on('click', 'a[data-path]', a_click);
}