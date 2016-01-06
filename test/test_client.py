# -*- coding:utf-8 -*-
import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for, request
import re

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		self.client = self.app.test_client(use_cookies=True)
		# Flask 测试客户端对象，在对象上调用方法向程序发起请求
		# use_cookies=True ，可以发送、接受 cookie。能够使用 cookie 的功能记住请求之间的上下文。可以启用用户会话

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get(url_for('main.index')) 
		# 在测试客户端上调用 get 方法，向首页发起请求，得到 FlaskResponse 对象，内容是对应视图函数的响应
		self.assertTrue('Guest' in response.get_data(as_text=True))
		# 通过 response.get_data 获取响应主体，在主体中搜索是否包含 Stranger
		# get_data 默认得到的响应主体是一个数组，传入 as_text=True 得到易于处理的 Unicode 字符串
		# print response
		# <Response 3073 bytes [200 OK]>
		# print response.get_data
		# <bound method Response.get_data of <Response 3073 bytes [200 OK]>>

	# 模拟注册、登陆、退出
	def test_register_and_login(self):
		# 注册新账号
		response = self.client.post(url_for('auth.register'), data={
													'email': 'john@example.com', 
													'username': 'john',
													'password': 'cat',
													'password_con': 'cat'
													})
		# 先向注册路由用 post 方法提交一个表单。
		# post() 方法的 data 参数是个字典,包含 表单中的各个字段 ,各字段的名字必须严格匹配定义表单时使用的名字。
		# 由于 CSRF 保护已经在测试配置中禁用了,因此无需和表单数据一起发送。
		
		# print response.status_code
		self.assertTrue(response.status_code == 302)
		# 如果注册数据可用,会返回一个重定向,把用户转到 登录页面。为了确认注册成功,测试会检查响应的状态码是否为 302,这个代码表示重定向。

		# 新账号登陆
		response = self.client.post(url_for('auth.login'), data={
													'email': 'john@example.com',
													'password': 'cat'
													}, follow_redirects=True)
		# 向 /auth/login 路由发起 POST 请求。
		# 调用 post() 方法时指定了参数 follow_ redirects=True,让测试客户端和浏览器一样,自动向重定向的 URL 发起 GET 请求。
		data = response.get_data(as_text=True)
		# 成功登录后的响应应该是一个页面,显示一个包含用户名的欢迎消息,并提醒用户需要进行账户确认才能获得权限。
		# 为此,两个断言语句被用于检查响应是否为这个页面。
		
		# print data
		self.assertTrue(re.search('Hello,\s+john', data))
		"""
		直接搜索字符串 'Hello, john!' 并没有用,因为这个字符串由 动态部分 和 静态部分 组成,而且 两部分之间有额外的空白。
		为了避免测试时空白引起的问题,我们使用 更为灵活的正则表达式。
		`\s` 包括空格、制表符、换页符等空白字符的其中任意一个
		"""
		self.assertTrue('A confirmation email has been sent to you by email' in data)

		# 发送确认令牌，进行确认
		user = User.query.filter_by(email='john@example.com').first()
		token = user.generate_confirmation_token()
		# print token
		# print user.confirmed
		# print url_for('auth.confirm', token=token)
		response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
		data = response.get_data(as_text=True)
		# print data
		self.assertTrue('You have confirmed your account. Thanks!' in data)

		# 退出
		response = self.client.get(url_for('auth.logout'), follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You have been logged out.' in data)

