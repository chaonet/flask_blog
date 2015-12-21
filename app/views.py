# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect,    session, url_for, request, g
# g: 存储登录的用户信息

from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post

from app import app,   db, login_manager, send_email
from .forms import LoginForm, RegistrationForm, Renewpassword, Renewmail, Newpassword, Newpassword_con

# 角色验证
from decorators import admin_required, permission_required
from .models import Permission

# 首页
@app.route('/')
@app.route('/index')
def index():
    # user = {'nickname': 'Miguel'}
    # print current_user.is_anonymous
    if session.get('name'):
        user=session.get('name')
    else:
        user='Guest'

    return render_template('index.html', title='Home', user=user)
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
            
            # 非登录情况下，访问 logout 页面，会跳转到登录页面，url：
            # http://127.0.0.1:5000/login?next=%2Flogout

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
        db.session.commit()
        # 即便通过配置,程序已经可以在请求末尾自动提交数据库变化,这里也要添加 db.session.commit() 调用。
        # 因为，提交数据库之后才能赋予新用户 id 值,而确认令 牌需要用到 id,所以不能延后提交。
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('login')) # 重定向到登陆页面, 让用户登陆。向 login url 发送 get 请求。
    return render_template('register.html', form=form)

# 令牌确认页面
@app.route('/confirm/<token>')
@login_required # 已登录用户才能访问，所以对于未登录用户，会自动跳转到登录页面，登录后，通过 next 再自动跳转回来，完成状态修改
def confirm(token):
    if current_user.confirmed: # 检查状态是否是 已经确认
        return redirect(url_for('index')) # 直接重定向到主页
    if current_user.confirm(token): # 令牌确认，完全在 User 模型中完成，视图函数只需调用 confirm() 方法，完成对用户的状态属性 转换。
        flash('You have confirmed your account. Thanks!')  # 完成账号确认，状态
    else:
        flash('The confirmation link is invalid or has expired.') # 连接无效 或 超时。需要重发确认邮件……
    return redirect(url_for('index'))

# 请求钩子
@app.before_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and  \
    request.endpoint[0:7] != 'confirm' and request.endpoint[0:6] != 'logout' and request.endpoint[0:6] != 'index':
    #对于已经登录、没有确认、请求的页面不是令牌页面的 请求
        # return redirect(url_for('unconfirmed'))
        # print request.endpoint[0:6] is 'logout'
        return render_template('unconfirmed.html')
        # 重定向到 未确认页面

# # 未确认页面
# @app.route('/unconfirmed')
# def unconfirmed():
#     if current_user.is_anonymous or current_user.confirmed: # 游客，或已经确认的用户，直接跳到主页
#         return redirect(url_for('index'))
#     return render_template('unconfirmed.html')

# 重新产生、发送账号确认邮件，即 令牌
@app.route('/confirm')
@login_required # 确保能够获取用户信息，知道往哪儿发送邮件
def confirmresend():
    # print current_user
    # # <User u'chao'>
    token = current_user.generate_confirmation_token()
    # print token
    # print current_user.email
    # xuchaorfc@gmail.com
    # print current_user
    send_email(current_user.email, 'Confirm Your Account', 'confirm', user=current_user, token=token)
    flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('index'))

# 重设密码
@app.route('/renew_password', methods = ['GET', 'POST'])
@login_required
def renew_password():
    form = Renewpassword()
    head = 'Renew password'
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data): # 验证旧密码是否正确
            current_user.password = form.new_password.data # 将新密码保存到数据库
            flash('Success to renew password')
            return redirect(url_for('index'))
        else:
            flash('Wrong old password')
            form.new_password.data = ''
            form.new_password_con.data = ''
    return render_template('renew.html', form=form, head=head)


@app.route('/renew_email', methods = ['GET', 'POST'])
@login_required
def renew_email():
    form = Renewmail()
    head = 'Renew mail'
    if form.validate_on_submit():
        new_email = form.new_email.data
        session['new_email'] = new_email
        token = current_user.generate_confirmation_token(new_email=new_email)
        send_email(new_email, 'Confirm Your new email', 'confirmmail', user=current_user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('index'))
    return render_template('renew.html', form=form, head=head)

# 令牌确认页面
@app.route('/confirmmail/<token>')
@login_required # 已登录用户才能访问，所以对于未登录用户，会自动跳转到登录页面，登录后，通过 next 再自动跳转回来，完成状态修改
def confirmmail(token):
    new_email = session['new_email']
    if current_user.confirmmail(token, new_email): # 令牌确认，完全在 User 模型中完成，视图函数只需调用 confirm() 方法，完成对用户的状态属性 转换。
        flash('You have confirmed your new email. Thanks!')  # 完成账号确认，状态
    else:
        flash('The confirmation link is invalid or has expired.') # 连接无效 或 超时。需要重发确认邮件……
    return redirect(url_for('index'))

# 找回密码
@app.route('/newpassword', methods = ['GET', 'POST'])
def changepassword():
    form = Newpassword()
    head = 'Input your register email'
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        session['email'] = email
        # TypeError: <User u'chao'> is not JSON serializable
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(email, 'Change Your password', 'changepassword', user=user, token=token)
            flash('A confirmation email has been sent to you by email.')
            return redirect(url_for('index'))
        flash('The email no exist.')
    return render_template('renew.html', form=form, head=head)

# 令牌确认页面
@app.route('/confirmpassword/<token>', methods = ['GET', 'POST'])
def confirmpassword(token):
    email = session['email']
    user = User.query.filter_by(email=email).first()
    form = Newpassword_con()
    head = 'Input your new password'
    if user.confirmpassword(token):
        if form.validate_on_submit():
            user.password = form.password.data
            flash('Your password is changed.')
            return redirect(url_for('index'))
        return render_template('renew.html', form=form, head=head) # 渲染`renew`给用户，表单提交时，url 保持为当前页面
    return render_template('index.html')


@app.route('/admin')
@login_required
@admin_required # 管理员角色验证
def for_admins_only():
    return 'For administrators!'

@app.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS) # 其他用户角色认证
def for_moderators_only():
    return 'For comment moderators!'

