# -*- coding:utf-8 -*-
from selenium import webdriver
import unittest
from app import create_app, db
from app.models import User, Role, Post
from flask import url_for, request, json
import re
import logging
import threading

class SeleniumTestCase(unittest.TestCase):
	client = None

	@classmethod # 类方法，不需要 self 参数，但第一个参数必须是 表示自身类的cls 参数
	def setUpClass(cls): # 在这个类中的全部测试运行前执行
		# 启动 Chrome
		try:
			cls.client = webdriver.Chrome() # 在类方法中，通过 cls 参数调用类的方法、属性
		except:
			pass

		# 如果无法启动浏览器,则跳过这些测试
		if cls.client:
			# 创建程序
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			# 日志？？
			import logging
			logger = logging.getLogger('werkzeug') # 获取logger对象
			logger.setLevel('ERROR') # 设置获取 ERROR 级别的日志

			# 创建数据库，使用一些虚拟数据填充
			db.create_all()
			Role.insert_roles()
			User.generate_fake(10)
			Post.generate_fake(10)

			# 添加管理员用户
			admin_role = Role.query.filter_by(permissions=0xff).first()
			admin = User(email='john@example.com', username='john', password='cat', role=admin_role, confirmed=True)
			db.session.add(admin)
			db.session.commit()

			# 在线程中启动 Flask 服务器
			threading.Thread(target=cls.app.run).start() # 启用程序

	@classmethod # 类方法，不需要 self 参数，但第一个参数必须是 表示自身类的cls 参数
	def tearDownClass(cls):  # 在这个类中的全部测试运行完成后执行
		if cls.client:
			# 关闭 Flask 服务器和浏览器
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.close()

			# 删除测试数据
			db.drop_all()
			db.session.remove()

			# 清空程序上下文
			cls.app_context.pop()

	def setUp(self): # 在每个测试运行之前执行
		if not self.client:
			self.skipTest('Web browser not available')

	def tearDown(self):
		pass

	def test_admin_home_page(self):
		# 进入首页
		self.client.get('http://localhost:5000/') # 用 GET 方式获取 'http://localhost:5000/' 页面
		self.assertTrue(re.search('Hello,\s+Guest', self.client.page_source)) # 在页面源代码中查找指定字符串

		# 进入登陆页
		self.client.find_element_by_link_text('Login').click()
		self.assertTrue('Blog - Login' in self.client.page_source)

		# 登陆
		self.client.find_element_by_name('email').send_keys('john@example.com') # 查找名称为 email 的元素，输入值
		self.client.find_element_by_name('password').send_keys('cat')
		self.client.find_element_by_name('submit').click() # 查找名称为 submit 的按钮，点击
		self.assertTrue(re.search('Hello,\s+john', self.client.page_source)) # 在收到的源代码中查找指定字符串

		# 进入用户个人资料页面
		self.client.find_element_by_link_text('Profile').click() # 查找名为Profile的带链接的文本，点击
		self.assertTrue('<h1>john</h1>' in self.client.page_source)



