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
virtualenv flask_blog
. ./bin/activate
pip install -r requirements.txt
```

## 本地构建方法

```
# 创建本地 SQLite 数据库
python run.py db upgrade

# 在本地运行，并在本地 5000 端口启动测试服务器
# 访问 http://127.0.0.1:5000/ 观察效果
python run.py runserver
```

## 在 Heroku 部署

[Heroku 部署教程](http://www.jianshu.com/p/7bc34e56fa39)

## 注意

头像使用[Gravatar](http://gravatar.com/), 加载头像需要翻墙

- 建议使用 google 的 Lantern
- Shadowsocks 的默认配置无法实现
