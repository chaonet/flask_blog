# -*- coding:utf-8 -*-
from flask import render_template, jsonify

from . import main

@main.app_errorhandler(404) # 404 和 500 错误由 Flask 自己生成的, 所以需要在主体上修改，以实现用 JSON 响应错误
def page_not_found(e):
	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html: # 筛选接受的 mime 类型
		response = jsonify({'error': 'not found'})
		response.status_code = 404
		return response
	return render_template('404.html'), 404
