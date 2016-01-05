# -*- coding:utf-8 -*-
import unittest
from app.models import User, Role, Permission, AnonymousUser

class UserModelTestCase(unittest.TestCase):

	def test_password_setter(self): # 验证设置密码可以自动生成 hash
		u = User(password = 'cat')
		self.assertTrue(u.password_hash is not None) # 断言不为空

	def test_no_password_getter(self): # 验证密码没有 getter 属性
		u = User(password = 'cat')
		with self.assertRaises(AttributeError): # 证实会报出一个指定的异常
			u.password # 对 password 调用 getter 属性

	def test_password_verification(self): # 确认 密码验证 正常
		u = User(password = 'cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self): # 验证 密码的hash值 是随机生成的，不会重复
		u = User(password = 'cat')
		u2 = User(password = 'cat')
		self.assertTrue(u.password_hash != u2.password_hash)

	# def test_roles_and_permissions(self):
	# 	Role.insert_roles()
	# 	u = User(email='john@example.com', password='cat')
	# 	self.assertTrue(u.can(Permission.WRITE_ARTICLES))
	# 	self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))

