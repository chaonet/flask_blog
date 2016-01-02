# -*- coding:utf-8 -*-
sfrom flask import jsonify

def forbidden(message): # 辅助函数，用于 Web 服务器生成的错误状态码
	response = jsonify({'error': 'forbidden', 'message': message})
	response.status_code = 403
	return response
