# -*- coding:utf-8 -*-
from flask import Blueprint

from ..models import Permission

main = Blueprint('main', __name__) # 实例化 Blueprint ，创建蓝本。两个参数：蓝本名称、蓝本所在的包或模块

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import views # 导入路由，与蓝本关联

