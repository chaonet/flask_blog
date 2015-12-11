# -*- coding:utf-8 -*-
from flask import Flask # 导入类

app = Flask(__name__) # 创建实例，因为是导入，'__name__'是包名，作为 flask 寻找文件的目录
# print __name__ # app
from app import views
