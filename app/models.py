# -*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # 生成 具有过期时间的JSON Web签名(JSON Web Signatures,JWS)
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app # 程序上下文
from app import login_manager
from datetime import datetime
from app import db

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
    # posts = db.relationship('Post', backref='author', lazy='dynamic') # 在 Post 中插入 author 反向引用
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False) # 用户状态: 待确认/已确认
    name = db.Column(db.String(64)) # 真实姓名
    location = db.Column(db.String(64)) # 所在地
    member_since = db.Column(db.DateTime(), default=datetime.utcnow) # 注册日期
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) # 最后访问日期
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 外键，与 roles 的 id 列 建立联结，值为 roles.id 的值

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
        # 赋予角色
        if self.role is None: # 如果还没有角色
            if self.email == current_app.config['MAIL_USERNAME']: # 如果 邮箱是 管理员邮箱
                self.role = Role.query.filter_by(permissions=0xff).first() # 定义角色为 管理员(通过权限查找)。不能用 False，因为 Moderator 也是 False
            if self.role is None: # 如果角色还是空，说明不是管理员
                self.role = Role.query.filter_by(default=True).first() # 角色定义为用户，即 default 是  True。默认角色。

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
        print s
        print self
        print self.id
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

    def confirmmail(self, token, new_email):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)  # 检验收到的令牌字符串的 原始数据、过期时间
        except:
            return False
        if data.get('confirm') != self.id or data.get('new_email') != new_email: 
            return False
        self.email = new_email
        return True

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

    # def is_authenticated(self):
    # 	return True

    # def is_active(self):
    # 	return True

    # def is_anonymous(self):
    # 	return False

    # def get_id(self):
    # 	try:
    # 		return unicode(self.id)
    # 	except NameError:
    # 		return str(self.id)
    
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
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	#user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 外键使用 ForeignKey，指向 User 表的 id

	def __repr__(self):
		return '<Post %r>' % self.body

# 为了保持一致，对游客也提供这两个身份验证方法，不需要先检查用户是否登录，可以自由调用 current_user.can() 和 current_user.is_administrator()
class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

# ??
# 将 AnonymousUser 设为用户未登录时 current_user 的值
login_manager.anonymous_user = AnonymousUser
