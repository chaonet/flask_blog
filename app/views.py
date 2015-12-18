# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect,    session, url_for, request, g
# g: 存储登录的用户信息

from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post

from app import app,   db, login_manager
from .forms import LoginForm, RegistrationForm

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
@app.route('/login', methods = ['GET', 'POST']) # 接收 url 为 `/login`, HTTP 方式为 'GET' 和 'POST' 的请求
def login():

    form = LoginForm() # 创建实例，表示表单
    '''
['Meta', 'SECRET_KEY', 'TIME_LIMIT', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_errors', '_fields', '_get_translations', '_prefix', '_unbound_fields', '_wtforms_meta', 'csrf_enabled', 'csrf_token', 'data', 'errors', 'generate_csrf_token', 'hidden_tag', 'is_submitted', 'meta', 'openid', 'populate_obj', 'process', 'remember_me', 'validate', 'validate_csrf_data', 'validate_csrf_token', 'validate_on_submit']
    '''
    if form.validate_on_submit(): # 如果 通过 post 提交的表单，数据通过了所有验证器的检查
        user = User.query.filter_by(email=form.email.data).first() # 用表单中的 email 在 User 表中查询，返回第一行结果的数据
        if user is not None and user.verify_password(form.password.data): # 如果 数据库中有这个 email 注册的用户，且库中的 密码与 提交的表单相同
            login_user(user, form.remember_me.data) # 在 用户会话 中把用户标记为已登录。参数是要登录的用户,以及可选的“记住我”布尔值
            # 如果值为 False,那么关闭浏览器后 用户会话 就过期了,下次用户访问时要重新登录。
            # 如果值为 True,那么会在用户浏览器中写入一个长期有效的 cookie,使用这个 cookie 可以恢复用户会话
            return redirect(request.args.get('next') or  url_for('index'))
            # 当用户未登陆时，访问未授权的 URL ，会跳转显示登录表单
            # 此时 Flask-Login 会将这个访问的 URL 保存在 查询字符串 的 next 参数中,这个参数可从 request.args 字典中读取。
            # 当用户认证成功后，自动跳转到之前未成功访问的 URL。

            # 或者，直接跳转到 'index'
        flash('Invalid username or password.')
        # session['name'] = form.name.data 
        # return redirect(url_for('index'))

        # print form.name.data
        # form.name.data = '' # 重置表单的 name 字段内容
        
        # flask.session，一旦数据存储在会话对象中，以后来自同一客户端的请求都是可用的。
        # 数据保存在会话中，直到会话被明确地删除。
        # 为了实现记录会话的效果，Flask 为应用程序中每一个客户端设置不同的会话文件。
    return render_template('login.html', form=form)

# 退出，跳转到主页
@app.route('/logout')
@login_required # 保护路由，只允许已登陆用户访问。Flask-Login 提供的装饰器，将用户重定向到 登陆页面
def logout():
    logout_user() # 删除并重设用户会话
    flash('You have been logged out.')
    return redirect(url_for('index'))

# 注册页面
@app.route('/register', methods = ['GET', 'POST']) # 初次 get 请求获取空白表单，然后 post 请求提交填写后的表单
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data
                    )
        db.session.add(user) # 添加到会话，请求结束后自动提交到数据库
        flash('You can now login.')
        return redirect(url_for('login')) # 重定向到登陆页面, 让用户登陆。向 login url 发送 get 请求。
    return render_template('register.html', form=form)

