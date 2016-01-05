# -*- coding:utf-8 -*-
import unittest # Python 标准库中的 unittest 包

from flask import current_app # 导入程序上下文
from app import create_app, db

class BasicsTestCase(unittest.TestCase): # 定义一个继承自unittest.TestCase的测试用例类
    def setUp(self): # 在每个测试用例 使用前 做一些辅助工作，创建测试环境
        self.app = create_app('testing') # 使用测试配置创建程序
        self.app_context = self.app.app_context() # 激活程序上下文
        self.app_context.push() # 推送信息到程序上下文
        db.create_all() # 创建一个全新的数据库

    def tearDown(self): # 在每个测试用例 结束后 做一些辅助工作
        db.session.remove() # 删除与数据库的会话
        db.drop_all() # 删除测试用的数据库
        self.app_context.pop() # 删除测试用实例的上下文

    def test_app_exists(self): # 定义测试用例，名字以test开头
        self.assertFalse(current_app is None) # 调用 assertFalse 断言方法证实状态为 False
        
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

