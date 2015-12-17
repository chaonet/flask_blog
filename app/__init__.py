# -*- coding:utf-8 -*-
import os
from flask import Flask # 导入类
from flask.ext.sqlalchemy import SQLAlchemy # 从 flask 扩展中导入 SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand # 数据库迁移
from flask.ext.script import Manager

from flask.ext.mail import Mail

from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap # Bootstrap 客户端框架

from config import basedir

app = Flask(__name__) # 创建实例，因为是作为包被导入，'__name__'是包名，作为 flask 寻找文件的目录
# print __name__,2 # app
app.config.from_object('config') # 从对象 'config' 读取配置到`app.config`
db = SQLAlchemy(app) # 初始化数据库
# print dir(db)

lm = LoginManager()
# print lm
# <flask_login.LoginManager object at 0x1036899d0>
lm.init_app(app)

# 初始化 bootstrap
bootstrap = Bootstrap(app)

# email
mail = Mail(app)

# 数据库迁移
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand) # MigrateCommand 类通过参数名 `db` 调用

from app import views, models
