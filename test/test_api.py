# -*- coding:utf-8 -*-
import unittest
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Post
from flask import url_for, request, json

class APITestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def get_api_headers(self, username, password):
		# 辅助方法,返回所有请求都要发送的 通用首部 ,其中包含认证密令和 MIME 类型相关的首部。
		return {
			'Authorization': 'Basic ' + b64encode(
								(username + ':' + password).encode('utf-8')).decode('utf-8'),
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		}

	def test_guest(self): # 允许游客访问部分。email 为空，认为是匿名用户访问
		response = self.client.get(url_for('api.get_posts'),
											content_type='application/json')
		# print response
		self.assertTrue(response.status_code == 200)

	def test_unauthorized(self): # 拒绝未认证的用户的请求,返回 401 错误码
		response = self.client.get(url_for('api.get_posts'),
											content_type='application/json',
											headers=self.get_api_headers('john@test.com', 'cat'))
		# print response
		self.assertTrue(response.status_code == 401)

	def test_posts(self):
		# 添加用户
		r = Role.query.filter_by(name='User').first() # 确认有 User 这个角色
		self.assertIsNotNone(r)
		u = User(email='john@example.com', password='cat', confirmed=True, role=r) # 创建已确认的用户
		db.session.add(u)
		db.session.commit()

		# 写一篇文章
		response = self.client.post(
			url_for('api.new_post'),
			headers=self.get_api_headers('john@example.com', 'cat'),
			data=json.dumps({'body': 'body of the *blog* post'}))
		self.assertTrue(response.status_code == 201)
		url = response.headers.get('Location')
		self.assertIsNotNone(url)

		# 获取发布的文章
		response = self.client.get(
			url,
			headers=self.get_api_headers('john@example.com', 'cat'))
		self.assertTrue(response.status_code == 200)
		json_response = json.loads(response.data.decode('utf-8'))
		self.assertTrue(json_response['url'] == url)
		self.assertTrue(json_response['body'] == 'body of the *blog* post')
		# print json_response['body_html']
		self.assertTrue(json_response['body_html'] == '<p>body of the <em>blog</em> post</p>')

