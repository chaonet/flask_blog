# -*- coding:utf-8 -*-
import os
from flask import Flask, render_template

# 导入 Flask 扩展
from flask.ext.sqlalchemy import SQLAlchemy # 从 flask 扩展中导入 SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand # 数据库迁移
from flask.ext.script import Manager
from flask.ext.moment import Moment
from flask.ext.mail import Mail, Message
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap # Twitter 的开源客户端框架， Bootstrap
from flask.ext.pagedown import PageDown # 客户端 Markdown 到 HTML 的转换程序

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
# print lm
# <flask_login.LoginManager object at 0x1036899d0>

def create_app(config_name):
	app = Flask(__name__) # 创建实例，因为是作为包被导入，'__name__'是包名，作为 flask 寻找文件的目录
# print __name__,2 # app
	app.config.from_object(config[config_name]) # 从文件对象 'config' 读取配置到`app.config`
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	from .main import main as main_blueprint # 注册蓝本
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint # 注册 认证蓝本
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	# 如果不是开发、测试环境，并且 SSL 没有被关闭
	if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
		from flask.ext.sslify import SSLify
		sslify = SSLify(app) # 让程序将拦截发往 http:// 的请求，重定向到 https://

	return app

# from app import views, models
