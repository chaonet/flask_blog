# -*- coding:utf-8 -*-
#! env python
import os

from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('defalut') # 创建程序
manager = Manager(app)  # 初始化 Flask-Script
migrate = Migrate(app, db) # 初始化 Flask-Migrate

def make_shell_context(): # 初始化 为 Python shell 定义的上下文
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()