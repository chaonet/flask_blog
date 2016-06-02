## flask_blog
学习[《Flask Web开发：基于Python的Web应用开发实战》](http://book.douban.com/subject/26274202/)开发的网站

发布: [flask-blog-chaonet](https://flask-blog-chaonet.herokuapp.com/)

部分开发经验总结:

- [Flask系列：工作流程](http://www.jianshu.com/p/8677d18de601)
  - [WSGI](http://www.jianshu.com/p/34ee01d85b0a)
  - [socket 和 网络I/O模型](http://www.jianshu.com/p/7ac69db65a0e)
- [Flask系列：模板](http://www.jianshu.com/p/2e391908bc35)
- [Flask系列：表单](http://www.jianshu.com/p/3b8d0d961fd3)
- [Flask系列：数据库](http://www.jianshu.com/p/0c88017f9b46)

## 开发环境

```
Python 2.7.9
OS 10.10.5
```

## 构建环境配置

```
# 下载源码
git clone git@github.com:chaonet/flask_blog.git
# 或者通过 HTTPS 下载:
git clone https://github.com/chaonet/flask_blog.git

cd flask_blog

# 安装依赖
virtualenv venv-foo
. ./venv-foo/bin/activate
pip install -r requirements.txt

Ubuntu/Debia
pip install前先使用sudo apt-get install libpq-dev python-dev
```
## 使用：
```
# 创建本地 SQLite 数据库, 将数据库迁移到最新版本
python run.py db upgrade

# 本地运行，在本地 5000 端口启动测试服务器
# 访问 http://127.0.0.1:5000/ 观察效果
python run.py runserver

`ctrl + c`退出
```
## 其他功能：
```
# 进行代码测试
python run.py test

`test_register_and_login (test_client.FlaskClientTestCase) ... FAIL`

需要在`config.py`中配置 email 客户端参数，这个应用中使用 QQ 邮箱，并且账号密码从环境变量中读取

    # 作为email第三方客户端的参数配置，与 服务器 建立连接，并将邮件传给 服务器，由服务器发送出去
    MAIL_SERVER = 'smtp.qq.com' 
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


# 启动程序 ,并在终端显示每条请求的分析数据,其中包含运行最慢的 25 个函数
python run.py profile

# 创建迁移仓库
# 将向应用添加一个`migrations`文件夹，存放迁移脚本
python run.py db init

# 基于 Flask 应用的上下文，运行 shell，可以与数据库交互
python run.py shell

# 自动创建迁移脚本
python run.py db migrate -m 'migration' 
```

## 在 Heroku 部署

[Heroku 部署教程](http://www.jianshu.com/p/7bc34e56fa39)

## 注意

头像使用[Gravatar](http://gravatar.com/), 加载头像需要翻墙

- 建议使用 google 的 Lantern
- Shadowsocks 的默认配置无法实现
