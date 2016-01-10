# -*- coding:utf-8 -*-
#! env python
import os

from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default') # 创建程序，配置从环境变量获取，或使用默认值
manager = Manager(app)  # 初始化 Flask-Script
migrate = Migrate(app, db) # 初始化 Flask-Migrate

def make_shell_context(): # 初始化 为 Python shell 定义的上下文
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

COV = None
if os.environ.get('FLASK_COVERAGE'): # 如果设置了覆盖检测
    import coverage # 导入 coverage
    COV = coverage.coverage(branch=True, include='app/*') # 启动覆盖检测引擎
    # branch 的覆盖检测，除了通常的语句，还包括 检查每个条件语句的 True 和 False 分支是否执行了
    # include 限制分析的文件范围，名称匹配模式的文件列表，匹配的文件将被测量覆盖率
    COV.start()

@manager.command
def test(coverage=False): # 向 run.py 脚本添加一个自定义命令。 函数名就是命令名
# Flask-Script 根据参数名确定选项名,并据此向函数中传入 True 或 False。
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
    # 如果命令行传递了coverage，而且 PATH 环境变量没有设置 FLASK_COVERAGE
        import sys
        os.environ['FLASK_COVERAGE'] = '1' # 设定环境变量 FLASK_COVERAGE
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    """
    函数执行一个新的程序，然后用新的程序替换当前子进程的进程空间，而该子进程从新程序的main函数开始执行。 重启子进程
    在Unix下，该新程序的进程id是原来被替换的子进程的进程id。在原来子进程中打开的所有描述符默认都是可用的，不会被关闭。
    """
    # os.execvp(file, args) , 接受的参数是以一个list或者是一个tuple表示的参数表

    # ➜  flask_blog git:(rest) ✗ python run.py shell
    # >>> import sys
    # >>> sys.executable
    # '/Users/chao/Desktop/projects/flask/bin/python'
    # 一个字符串，给出Python解释器的绝对路径
    # >>> sys.argv
    # ['run.py', 'shell']
    # >>> [sys.executable] + sys.argv
    # ['/Users/chao/Desktop/projects/flask/bin/python', 'run.py', 'shell']

    import unittest
    test = unittest.TestLoader().discover('test') # 指定开始目录，在其子目录中递归查找所有测试模块，返回一个包含所有模块信息的 TestSuite  对象
    unittest.TextTestRunner(verbosity=2).run(test) # 在代码中使用 TextTestRunner 运行测试。
    # verbosity = 1，只有结果；verbosity = 2，输出详细的信息
    if COV:
        COV.stop()
        COV.save()
        print 'Coverage Summary:'
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage') # 覆盖检测保存的目录
        COV.html_report(directory=covdir) # 导出 HTML 格式的报告
        print 'HTML version: file://%s/index.html' % covdir
        COV.erase()

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

# 代码分析器
@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    # 需要分析的 WSGI 应用，
    app.run()

"""
使用 python manage.py profile 启动程序后,终端会显示每条请求的分析数据,其中包含运行最慢的 25 个函数。
--length 选项可以修改报告中显示的函数数量。
如果指定了 --profile-dir 选项,每条请求的分析数据就会保存到指定目录下的一个文件中。
"""

# 部署的命令
@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role

    # 把数据库迁移到最新修订版本
    upgrade()

    # 创建用户角色
    Role.insert_roles()


if __name__ == '__main__':
    manager.run()