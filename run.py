# -*- coding:utf-8 -*-
#! env python
import os

from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('default') # 创建程序
manager = Manager(app)  # 初始化 Flask-Script
migrate = Migrate(app, db) # 初始化 Flask-Migrate

def make_shell_context(): # 初始化 为 Python shell 定义的上下文
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(): # 向 run.py 脚本添加一个自定义命令。 函数名就是命令名
	"""Run the unit tests."""
	import unittest
	test = unittest.TestLoader().discover('test') # 指定开始目录，在其子目录中递归查找所有测试模块，返回一个包含所有模块信息的 TestSuite  对象
	unittest.TextTestRunner(verbosity=2).run(test) # 在代码中使用 TextTestRunner 运行测试。
	# verbosity = 1，只有结果；verbosity = 2，输出详细的信息
'''
➜  flask_blog git:(rest) ✗ python run.py test
test_app_exists (test_basics.BasicsTestCase) ... ok
test_app_is_testing (test_basics.BasicsTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.049s

OK
➜  flask_blog git:(rest) ✗ python run.py test
..
----------------------------------------------------------------------
Ran 2 tests in 0.050s

OK
'''

if __name__ == '__main__':
	manager.run()