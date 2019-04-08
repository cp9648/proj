# 项目说明文档

* 添加初始用户
```shell
python dev-init-data.py
```
* 运行
```shell
python run.py
```
* 安装Python需要的包
```shell
pip install -r requirements.txt
```

## 辅助调试插件：
* flask-debugtoolbar
    - [Flask-DebugToolbar](https://flask-debugtoolbar.readthedocs.io/)
        + 安装命令: 
        ```bash
        pip install flask-debugtoolbar
        ```
        + 使用代码：
        ```python
        from flask_debugtoolbar import DebugToolbarExtension
        # 省略若干代码
        toolbar = DebugToolbarExtension(app)
        ```

## 第三方前端库
* jQuery
    - [jquery-1.12.4.js](http://code.jquery.com/jquery-1.12.4.js)
    - [jquery-1.12.4.min.js](http://code.jquery.com/jquery-1.12.4.min.js)
* amazeui
    - [Breadcrumb\(面包屑导航\)](http://www.amazeui.org/css/breadcrumb)
    - [JS 插件-Cookie](http://www.amazeui.org/javascript/cookie)
* jQuery-File-Upload
    - [cdn](https://cdnjs.com/libraries/blueimp-file-upload)
    - [GitHub-Wiki](https://github.com/blueimp/jQuery-File-Upload/wiki)
    - [flask-file-uploader](https://github.com/ngoduykhanh/flask-file-uploader)
        + 在Git-Bash里执行： `git clone https://github.com/ngoduykhanh/flask-file-uploader.git`

## 主要知识
* jQuery:
    - [`closest()`方法](http://www.css88.com/jqapi-1.9/closest/): 选取父级元素（返回结果包含当前节点）
    - [`parents()`方法](http://www.css88.com/jqapi-1.9/parents/): 选取父级元素（返回结果不包含当前节点，从父级元素开始）
* css:
    - `cursor: pointer;` 鼠标手型
* html:
    - `<a href="javascript:;">空链接</a>` js空链接（页面不会跳转）
    - `<a href="#">空链接</a>` 锚点空链接（页面会跳转）
* js:
    - `Array`:
        + `unshift()`: 向数组开头添加元素。（ http://www.w3school.com.cn/js/jsref_unshift.asp ）
        + `push()`: 向数组末尾追加元素。（ http://www.w3school.com.cn/js/jsref_push.asp ）
        + `join()`: （用传递个join的字符）将数组连接成一个字符串
        + `length`: 获取数组的长度
    - `arguments`: 在函数（function）中使用，获取调用函数时传递给函数的参数。（数组类型）。
    - `String`：
        + `replace(pattern, func)`: 字符串对象的`replace()`方法，支持使用正则表达式替换。（ http://www.w3school.com.cn/js/jsref_replace.asp ）
        + `substr(start_index, length)`: 字符串截取。（ http://www.w3school.com.cn/js/jsref_substr.asp ）
* [$.ajax](http://www.w3school.com.cn/jquery/ajax_ajax.asp):
    - url: 发送请求的地址
    - type: 发送HTTP请求的方法（GET、POST等）
    - data: 发送的数据（类似dict的结构）
    - dataType: 服务器响应的数据的类型（结构，可选值有：html、text、script等）
    - success: 请求成功之后调用的函数（向函数中传递服务器返回的数据）
    - error: 请求失败之后调用的函数
    - headers: 发送请求时，传递的请求头（类似dict的结构）（一般不需要）
* $.get(url, data, success) （$.ajax，type为'GET'时简写）
* $.post(url, data, success)（$.ajax，type为'POST'时简写）