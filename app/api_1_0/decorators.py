# -*- coding:utf-8 -*-
from functools import wraps
from flask import g

from .errors import forbidden
from ..models import Permission

# 检查常规权限
def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_functions(*args, **kwargs):
			if not g.current_user.can(permission): #
				return forbidden('Insufficient permissions') #
			return f(*args, **kwargs)
		return decorated_functions
	return decorator

# 专用于检查管理员权限
def admin_required(f):
	return permission_required(Permission.ADMINISTER)(f)
