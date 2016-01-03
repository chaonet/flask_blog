# -*- coding:utf-8 -*-
from flask import jsonify
from ..exceptions import ValidationError
from . import api

def forbidden(message): # 辅助函数，用于 Web 服务器生成的错误状态码
	response = jsonify({'error': 'forbidden', 'message': message}) # 响应的主体，JSON 格式，设定内容
	response.status_code = 403 # 设定状态码
	return response

def unauthorized(message):
	response = jsonify({'error': 'unauthorized', 'message': message})
	response.status_code = 401
	return response

# 全局的异常处理程序, 向客户端提供适当的响应，处理 ValidationError 这个异常
# 对于 errorhandler 修饰器，只要抛出了制定类的异常，就会调用被修饰的函数
# 这里仅针对蓝本中路由抛出的异常
@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])
