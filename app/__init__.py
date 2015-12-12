# -*- coding:utf-8 -*-
from flask import Flask # 导入类

apps = Flask(__name__) # 创建实例，因为是作为包被导入，'__name__'是包名，作为 flask 寻找文件的目录
# print __name__,2 # app
from app import views
