# -*- coding:utf-8 -*-
# 相当于 django 的 `setting.py`

# Flask-SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__)) # 项目根目录
# print __file__
# /Users/chao/Desktop/projects/flask/flask_blog/config.py
# print basedir
# /Users/chao/Desktop/projects/flask/flask_blog

class Config: # 通用的基类
    # Flask-WTF
    CSPR_ENABLED = True # 启用 CSPR (跨站请求伪造) 保护，在表单中使用，隐藏属性
    SECRET_KEY = 'this-is-safe-and-you-never-guess-it' # 建立一个加密的令牌，验证表单

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每次请求结束后, 自动提交数据库中的变动

    FLASKY_POSTS_PER_PAGE=10
    FLASKY_FOLLOWERS_PER_PAGE=1
    FLASKY_COMMENTS_PER_PAGE=10

    # 作为email第三方客户端的参数配置，与 服务器 建立连接，并将邮件传给 服务器，由服务器发送出去
    MAIL_SERVER = 'smtp.qq.com' 
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # print MAIL_USERNAME
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # print MAIL_PASSWORD

    SQLALCHEMY_RECORD_QUERIES = True # 启用记录查询统计
    FLASKY_DB_QUERY_TIMEOUT = 0.0001 # 查询耗时的阈值，0.5s

    @staticmethod
    def init_app(app):
        pass

    SSL_DISABLE = True # 默认关闭 SSL

class DevelopmentConfig(Config): # 开发专用配置
    DEBUG = True

    # [sqlite](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#sqlite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') # 数据库文件的路径、文件名
    # print SQLALCHEMY_DATABASE_URI
    # sqlite:////Users/chao/Desktop/projects/flask/flask_blog/app.db
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') # 文件夹，保存`SQLAlchemy-migrate`数据文件，也就是迁移策略文件
    # print SQLALCHEMY_MIGRATE_REPO
    # /Users/chao/Desktop/projects/flask/flask_blog/db_repository

class TestingConfig(Config): # 测试专用配置
    TESTING = True

    # CSPR_ENABLED = False
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app_test.db') # 数据库文件的路径、文件名

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/app_produ' # 短路
    # 'sqlite:///' + os.path.join(basedir, 'app_pro.db'
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_USERNAME,
            toaddrs=[cls.MAIL_USERNAME],
            subject='Application Error',
            credentials=credentials,
            secure=secure
            )
        mail_handler.setLevel(logging.ERROR) # 电子邮件日志记录器的日志等级被设为 logging.ERROR,所以只有发生严重错误时才会发送 电子邮件
        app.logger.addHandler(mail_handler) # 配置程序的日志记录器把错误写入电子 邮件日志记录器。

class HerokuConfig(ProductionConfig): # 继承自 ProductionConfig
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # 输出到 stderr，以便被 Heroku 抓取到 logs
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        SSL_DISABLE = bool(os.environ.get('SSL_DISABLE')) # 从环境变量中获取值，转换为布尔值，并覆盖基类的参数

        # 处理代理服务器的 HTTP 首部
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app) # 包装 app.wsgi_app ，进行中间件添加
        # 收到请求时,中间件有机会审查环境,在处理请求之前做些修改。

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}




