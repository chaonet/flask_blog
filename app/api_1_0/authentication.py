# -*- coding:utf-8 -*-
from flask import g, jsonify
from .errors import forbidden, unauthorized# forbidden_error

from . import api
from ..models import User, Post, AnonymousUser # 最低权限账号，游客

from flask.ext.httpauth import HTTPBasicAuth # HTTP 基本认证
auth = HTTPBasicAuth() # 创建一个 HTTPBasicAuth 类对象
# 只在 API 蓝本中使用，所以只在 蓝本中初始化，而不在程序包中初始化

# verify_password 如果定义了,这个回调函数将 被框架调用，用于验证客户端提供的 用户名和密码组合 是否有效
# 验证回调函数获取两个参数,用户名和密码,而且必须返回 True 或 False
@auth.verify_password
def verify_password(email_or_token, password): # 第一个参数是 电子邮件地址或认证令牌
	if email_or_token == '': # 如果客户端发送的 email 为空，认为是匿名用户访问
		g.current_user = AnonymousUser() # 将用户保存在 Flask 的全局对象 g 中
		return True

	if password == '': # 如果密码为空，假定 email_or_token 提供的是令牌
		g.current_user = User.verify_auth_token(email_or_token) # 对令牌进行认证
		g.token_used = True # 标记该用户已经获取过 token
		return g.current_user is not None # 是否有该用户

	user = User.query.filter_by(email = email_or_token).first() # 如果都不为空，按照常规的 邮箱和密码 进行认证
	if not user:
		return False

	g.current_user = user # 将用户保存在 Flask 的全局对象 g 中，使得 视图函数可以访问 ？？

	g.token_used = False # 标记该用户没有申请过 认证令牌

	return user.verify_password(password) # 使用 User 模型中现有的方法验证，如果正确，返回 True 否则 返回 False

# 如果认证密码不正确，服务器向客户端返回 401 错误，默认 Flask-HTTPAuth自 动生成这个状态码
# 可以自定义这个错误响应
"""
如果定义了，当需要向客户端发送身份验证错误消息, 这个回调函数将被框架调用。
这个函数的返回值 可以作为响应主体中的字符串 或 也可以作为 make_response 创建的响应对象的主体。
如果这个回调没有被提供，将生成一个默认的错误响应。
"""
@auth.error_handler # 未授权错误响应
def auth_error():
	return unauthorized('Invalid credentials')

# 由于这个蓝本的所有路由都需要 保护路由，所以在 before_request 中使用 login_required，以便应用到整个蓝本
@api.before_request
@auth.login_required # 保护路由，只允许已登陆用户访问。否则，将用户重定向到 登陆页面
def before_request():
	if not g.current_user.is_anonymous and not g.current_user.confirmed: # 注册、登陆，但还没确认 的用户
		return forbidden('Unconfirmed account') # 拒绝

# 将生成的 认证令牌 发送给客户端
@api.route('/token')
def get_token():
	if g.current_user.is_anonymous or g.token_used: # 如果是游客，或 已经有令牌了
		return unauthorized('Invalid credentials') # 拒绝
	return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600}) # JSON 的响应也有过期时间

