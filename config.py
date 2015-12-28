# -*- coding:utf-8 -*-
# 相当于 django 的 `setting.py`

# Flask-SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__)) # 项目根目录
# print __file__
# /Users/chao/Desktop/projects/flask/flask_blog/config.py
# print basedir
# /Users/chao/Desktop/projects/flask/flask_blog

# [sqlite](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#sqlite)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') # 数据库文件的路径、文件名
# print SQLALCHEMY_DATABASE_URI
# sqlite:////Users/chao/Desktop/projects/flask/flask_blog/app.db
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') # 文件夹，保存`SQLAlchemy-migrate`数据文件，也就是迁移策略文件
# print SQLALCHEMY_MIGRATE_REPO
# /Users/chao/Desktop/projects/flask/flask_blog/db_repository
SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每次请求结束后, 自动提交数据库中的变动


# 作为email第三方客户端的参数配置，与 服务器 建立连接，并将邮件传给 服务器，由服务器发送出去
MAIL_SERVER = 'smtp.qq.com' 
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
# print MAIL_USERNAME
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
# print MAIL_PASSWORD

FLASKY_POSTS_PER_PAGE=10
FLASKY_FOLLOWERS_PER_PAGE=1
FLASKY_COMMENTS_PER_PAGE=10

# Flask-WTF
CSPR_ENABLED = True # 启用 CSPR (跨站请求伪造) 保护，在表单中使用，隐藏属性
SECRET_KEY = 'this-is-safe-and-you-never-guess-it' # 建立一个加密的令牌，验证表单

