# -*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # 生成 具有过期时间的JSON Web签名(JSON Web Signatures,JWS)
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask.ext.pagedown.fields import PageDownField # 与 TextAreaField 接口一致
from flask import current_app, request # 上下文
from app import login_manager
from datetime import datetime
from app import db

from markdown import markdown # markdown 到 html 转换
import bleach # 清理

import hashlib # 生成 MD5 值

# 定义几个操作，以及对应的值
class Permission:
         FOLLOW = 0x01
         COMMENT = 0x02
         WRITE_ARTICLES = 0x04
         MODERATE_COMMENTS = 0x08
         ADMINISTER = 0x80

class User(UserMixin, db.Model):
    __tablename__='users' # 自定义表名，隐藏属性
    id = db.Column(db.Integer, primary_key = True) # 主键，值由 Flask-SQLAlchemy 控制
    username = db.Column(db.String(64), index = True, unique = True) # index 为这列创建索引,提升查询效率; unique 不允许出现重复的值
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False) # 用户状态: 待确认/已确认
    name = db.Column(db.String(64)) # 真实姓名
    location = db.Column(db.String(64)) # 所在地
    about_me = db.Column(db.Text()) # 自我介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow) # 注册日期
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) # 最后访问日期
    avatar_hash = db.Column(db.String(32)) # 保存 email 的 MD5 值，以免每次 生成获取图片的URL ，都计算一次，耗费 CPU 资源
    # 可以从 POST 通过属性 author 引用 User 模型的属性和方法
    # post 的列表
    posts = db.relationship('Post', backref='author', lazy='dynamic') # 在 Post 中插入 author , 反向引用 ？？ 可以通过 post.author 获得 user 对象
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 外键，与 roles 的 id 列 建立联结，值为 roles.id 的值

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
        # 赋予角色
        if self.role is None: # 如果还没有角色
            if self.email == current_app.config['MAIL_USERNAME']: # 如果 邮箱是 管理员邮箱
                self.role = Role.query.filter_by(permissions=0xff).first() # 定义角色为 管理员(通过权限查找)。不能用 False，因为 Moderator 也是 False
            if self.role is None: # 如果角色还是空，说明不是管理员
                self.role = Role.query.filter_by(default=True).first() # 角色定义为用户，即 default 是  True。默认角色。

        if self.email is not None and self.avatar_hash is None: # 如果有email，并且 没有保存 MD5 值
            self.avatar_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # 身份验证
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions # 对实际权限和查询的权限，进行按位 与 操作，然后与查询的权限比较

    # 单独判断是否管理员身份
    def is_administrator(self): # 判断是否是管理员
        return self.can(Permission.ADMINISTER)

    # Python 内置装饰器，将一个getter方法变成属性。
    # 同时 @property 本身又创建了另一个装饰器@password.setter，负责把一个setter方法变成赋值属性
    @property 
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    # 设置密码时，获取密码，生成 散列值 保存到数据库，防止密码泄露
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 将用户登陆时输入的密码 进行散列值计算 并 与注册时填写的密码散列值 比较，检查是否相同
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 生成确认令牌
    def generate_confirmation_token(self, expiration=3600, new_email=None): 
        s = Serializer(current_app.config['SECRET_KEY'], expiration) # 接受 一个密钥 和 过期时间，1小时
        return s.dumps({'confirm': self.id, 'new_email': new_email}) # 返回 为 {'confirm': self.id} 生成的令牌
    
    # 确认用户发来的令牌
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # 检验收到的令牌字符串的 原始数据、过期时间
        except:
            return False
        if data.get('confirm') != self.id: # 是否是为该用户的ID 生成的令牌，即使知道如何生成令牌，如果ID不对，也无法通过
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 确认email
    def confirmmail(self, token, new_email):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # 检验收到的令牌字符串的 原始数据、过期时间
        except:
            return False
        if data.get('confirm') != self.id or data.get('new_email') != new_email: 
            return False
        self.email = new_email

        # 更换邮箱时，自动生成 MD5 并保存
        self.avatar_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    # 确认 password
    def confirmpassword(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # 检验收到的令牌字符串的 原始数据、过期时间
        except:
            return False
        if data.get('confirm') != self.id: # 是否是为该用户的ID 生成的令牌，即使知道如何生成令牌，如果ID不对，也无法通过
            return False
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    # 刷新用户的最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow() # 调用函数，生成现在的时间，赋值
        db.session.add(self)

    # 通过 email 获取 gravatar 上对应的 头像
    def gravatar(self, size=100, default='identicon', rating='g'): # 设置默认值
        if request.is_secure: # SSL
            url = 'https://secure.gravatar.com/avatar'
        else:  # 普通
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest() # 将 email 转为全小写，用 utf-8 编码，生成 MD5
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(url=url, hash=hash, size=size, default=default, rating=rating) # 生成请求 URL

    # 用 forgery_by 批量产生虚拟数据
    @staticmethod
    def generate_fake(count=100): # 传入变量，值 100
        from sqlalchemy.exc import IntegrityError # 异常类 (exception class), 完整性异常类
        from random import seed
        import forgery_py # 用于伪造数据

        seed() # 使用当前系统时间初始化随机数生成器的种子
        """
        forgery_py.forgery.address
        forgery_py.forgery.basic  
        forgery_py.forgery.currency
        forgery_py.forgery.date
        forgery_py.forgery.internet
        forgery_py.forgery.lorem_ipsum
        forgery_py.forgery.name
        forgery_py.forgery.personal
        """
        for i in range(count):  # 进行 100 次 for 循环
            u = User( email=forgery_py.internet.email_address(),
                      username=forgery_py.internet.user_name(True),
                      password=forgery_py.lorem_ipsum.word(),
                      confirmed=True,
                      name=forgery_py.name.full_name(),
                      location=forgery_py.address.city(),
                      about_me=forgery_py.lorem_ipsum.sentence(),
                      member_since=forgery_py.date.date(True)
                    ) # 创建用户
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            """
            用户的电子邮件地址和用户名必须是唯一的,但 ForgeryPy 随机生成这些信息,因 此有重复的风险。
            如果发生了这种不太可能出现的情况,提交数据库会话时会抛出 IntegrityError 异常。
            这个异常的处理方式是,在继续操作之前回滚会话。
            由于 在循环中生成重复内容时,不会把用户写入数据库,因此生成的虚拟用户总数可能会比预期少。
            """
    # def is_authenticated(self):
    #   return True

    # def is_active(self):
    #   return True

    # def is_anonymous(self):
    #   return False

    # def get_id(self):
    #   try:
    #       return unicode(self.id)
    #   except NameError:
    #       return str(self.id)
    
    # 加载用户的回调函数
    # 获得 Unicode 形式的用户id，转换为整形并查找用户
    # 如果找到，返回用户读写，否则 None
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True) # 只有管理员才会设置为 True, 其他角色默认 False
    permissions = db.Column(db.Integer)  # 权限，允许的操作集合，通过叠加权限值得出
    users = db.relationship('User', backref='role')

    # 定义角色
    @staticmethod # python 内置的装饰器，定义静态方法，类似全局函数，不需要 self 参数，可由类或类的实例调用
    def insert_roles():
        roles = {
                'User': (Permission.FOLLOW |
                         Permission.COMMENT |
                         Permission.WRITE_ARTICLES, True), # 按位 `或运算`
                'Moderator': (Permission.FOLLOW |
                              Permission.COMMENT |
                              Permission.WRITE_ARTICLES |
                              Permission.MODERATE_COMMENTS, False),
                'Administrator':(0xff, False)
        }
        # {'Moderator': (15, False), 'Administrator': (255, False), 'User': (7, True)}
        for r in roles:
            role = Role.query.filter_by(name=r).first() # 通过角色名查找是否有该角色
            if role is None:  # 如果没有
                role = Role(name=r) # 创建这个角色
            role.permissions = roles[r][0] # 按照 roles 字典，设置权限
            role.default = roles[r][1] # 设置是否管理员
            db.session.add(role) # 添加到会话
        db.session.commit() # 提交所有会话

    def __repr__(self):
        return '<Role %r>' % self.name

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text) # 博客正文，不限长度
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # 发布博文的时间
    body_html = db.Column(db.Text) # 存放转换后的 HTML 代码
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 外键使用 ForeignKey，指向 User 表的 id

    # 用 forgery_by 批量产生虚拟数据
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py # 用于伪造数据

        seed() # 使用当前系统时间初始化随机数生成器的种子
        '''
        随机生成文章时要为每篇文章随机指定一个用户。为此,我们使用 offset() 查询过滤器。
        这个过滤器会跳过参数中指定的记录数量。
        通过设定一个随机的偏移值,再调用 first() 方法,就能每次都获得一个随机用户。
        '''
        user_count = User.query.count() # 获取用户的数量
        for i in range(count): # 循环次数为用户的数量, 产生与用户数量相同的虚拟博客
            u = User.query.offset(randint(0, user_count - 1)).first() # 选择虚拟博客的作者，通过在 user 中产生随机的整数偏移获得
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)), # a <= n <= b
                     timestamp=forgery_py.date.date(True), # 随机产生 datetime.date  对象
                     author=u
                )
            db.session.add(p)
            db.session.commit()


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
                                markdown(value, output_format='html'), 
                                tags=allowed_tags, strip=True))
    """
    真正的转换过程分三步完成。
    首先,markdown() 函数初步把 Markdown 文本转换成 HTML。 
    然后,把得到的结果和允许使用的 HTML 标签列表传给 clean() 函数。clean() 函数删除 所有不在白名单中的标签。
    最后,由 linkify() 函数完成,这个函数由 Bleach 提 供,把纯文本中的 URL 转换成适当的 <a> 链接。
      最后一步是很有必要的,因为 Markdown 规范没有为自动生成链接提供官方支持。
      PageDown 以扩展的形式实现了这个功能,因此 在服务器上要调用 linkify() 函数。
    """
    def __repr__(self):
        return '<Post %r>' % self.body

db.event.listen(Post.body, 'set', Post.on_changed_body) # 监听某个字段的某个事件，一旦触发，执行指定的函数
"""
on_changed_body 函数注册在 body 字段上,是 SQLAlchemy“set”事件的监听程序
只要这个类实例的 body 字段设了新值,函数就会自动被调用。
on_changed_body 函数 把 body 字段中的文本渲染成 HTML 格式,结果保存在 body_html 中,
自动且高效地完成 Markdown 文本到 HTML 的转换。
"""

# 为了保持一致，对游客也提供这两个身份验证方法，不需要先检查用户是否登录，可以自由调用 current_user.can() 和 current_user.is_administrator()
class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

# ??
# 将 AnonymousUser 设为用户未登录时 current_user 的值
login_manager.anonymous_user = AnonymousUser
