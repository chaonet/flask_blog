# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect,    session, url_for, request, g
# g: 存储登录的用户信息

from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post

from app import app,   db, lm
from .forms import LoginForm

# 首页
@app.route('/')
@app.route('/index')
def index():
    # user = {'nickname': 'Miguel'}
    if session.get('name'):
        user=session.get('name')
    else:
        user='Guest'
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
             'author': {'nickname': 'Susan'},
             'body': 'The Avengers movie was so cool'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts = posts)
    # return "Hello, World!"

# print __name__,3 # app.views

# 登录页面，填写表单、认证
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # print g.user
    # <flask_login.AnonymousUserMixin object at 0x10403b2d0>

    form = LoginForm() # 创建实例，表示表单
    # print dir(form)
    '''
['Meta', 'SECRET_KEY', 'TIME_LIMIT', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_errors', '_fields', '_get_translations', '_prefix', '_unbound_fields', '_wtforms_meta', 'csrf_enabled', 'csrf_token', 'data', 'errors', 'generate_csrf_token', 'hidden_tag', 'is_submitted', 'meta', 'openid', 'populate_obj', 'process', 'remember_me', 'validate', 'validate_csrf_data', 'validate_csrf_token', 'validate_on_submit']
    '''
    if form.validate_on_submit(): # 处理 post 请求，收集数据、填入字段并验证，如果没有问题，返回 True。
        session['name'] = form.name.data 
        return redirect(url_for('index'))

        # print form.name.data
        # form.name.data = '' # 重置表单的 name 字段内容
        
        # flask.session，一旦数据存储在会话对象中，以后来自同一客户端的请求都是可用的。
        # 数据保存在会话中，直到会话被明确地删除。
        # 为了实现记录会话的效果，Flask 为应用程序中每一个客户端设置不同的会话文件。
        

    return render_template('login.html', title='Sing In', form=form)


