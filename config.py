# -*- coding:utf-8 -*-
# 相当于 django 的 `setting.py`

# Flask-SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# print __file__
# /Users/chao/Desktop/projects/flask/flask_blog/config.py
# print basedir
# /Users/chao/Desktop/projects/flask/flask_blog

# [sqlite](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#sqlite)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') # 数据库文件的路径
# print SQLALCHEMY_DATABASE_URI
# sqlite:////Users/chao/Desktop/projects/flask/flask_blog/app.db
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') # 文件夹，保存`SQLAlchemy-migrate`数据文件，也就是迁移策略文件
# print SQLALCHEMY_MIGRATE_REPO
# /Users/chao/Desktop/projects/flask/flask_blog/db_repository

# Flask-WTF
CSPR_ENABLED = True # 启用 CSPR (跨站请求伪造) 保护，在表单中使用
SECRET_KEY = 'this-is-safe-and-you-never-guess-it' # 建立一个加密的令牌，验证表单

