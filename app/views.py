# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, abort,    session, url_for, request, g, current_app
# g: 存储登录的用户信息

from flask.ext.login import login_user, logout_user, current_user, login_required
from .models import User, Post, Role

from app import app,   db, login_manager, send_email
from .forms import LoginForm, RegistrationForm, Renewpassword, Renewmail, Newpassword, Newpassword_con, EditProfileForm, EditProfileAdminForm, PostForm

# 角色验证
from decorators import admin_required, permission_required
from .models import Permission

# 首页
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit(): # 如果有写的权限，而且提交的表单有效
        # 新文章对象的 author 属性值为表达式 current_user._get_current_object()。
        # current_user 由 Flask-Login 提供,和所有上下文变量一样,也是通过线程内的代理对象实现。 ？？
        # 这个对象的表现类似用户对象,但实际上却是一个轻度包装,包含真正的用户对象。 ？？
        # 数据库需要真正的用户对象,因此要调用 _get_current_object() 方法获取。
        post = Post(body=form.body.data, author=current_user._get_current_object()) # 为提交的文章 新建一个 Post 对象，
        db.session.add(post)
        return redirect(url_for('index'))
    # 渲染的页数从请求的查询字符串(request.args)中获取,如果没有明确指定,则默认渲染第一页。
    # 参数 type=int 保证参数无法转换成整数时,返回默认值。
    page = request.args.get('page', 1, type=int)
    # print page
    # 1

    # print request
    # <Request 'http://127.0.0.1:5000/' [GET]>

    # print request.args
    # http://127.0.0.1:5000/?2 第二页

    # 为了显示某页中的记录,要把 all() 换成 Flask-SQLAlchemy 提供的 paginate() 方法。
    # paginate() 方法的第一个参数是 第几页,也是唯一必需的参数。
    # 可选参数 per_page 用来指定 每页显示的记录数量;如果没有指定,则默认显示 20 个记录。
    # 可选参数 error_ out,当其设为 True 时(默认值),如果请求的页数超出了范围,则会返回 404 错误;如果 设为 False,页数超出范围时会返回一个空列表。
    
    # 为了能够很便利地配置每页显示的记录 数量,参数 per_page 的值从程序的环境变量 FLASKY_POSTS_PER_PAGE 中读取。
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)

    # print pagination
    # <flask_sqlalchemy.Pagination object at 0x1041dd790>

    posts = pagination.items
    
    # print posts
    # [<Post u'Nam nulla. Curabitur in libero ut massa volutpat convallis. Nullam sit amet turpis elementum ligula vehicula consequat.'>, <Post u'Duis bibendum, felis sed interdum venenatis, turpis enim blandit mi, in porttitor pede justo eu massa. Donec dapibus.'>]
    
    # posts = Post.query.order_by(Post.timestamp.desc()).all() # 文章列表按照时间戳进行降序排列。

    return render_template('index.html', form=form, posts=posts, pagination=pagination) # 渲染 博客编辑的表单 和 完整的博客文章列表, 分页
    # return "Hello, World!"

    """
    ImmutableMultiDict([])
    127.0.0.1 - - [23/Dec/2015 20:17:56] "GET / HTTP/1.1" 200 -
    ImmutableMultiDict([('2', u'')])
    127.0.0.1 - - [23/Dec/2015 20:18:39] "GET /?2 HTTP/1.1" 200 -
    ImmutableMultiDict([('3', u'')])
    127.0.0.1 - - [23/Dec/2015 20:26:57] "GET /?3 HTTP/1.1" 200 -
    ImmutableMultiDict([('4', u'')])
    127.0.0.1 - - [23/Dec/2015 20:26:54] "GET /?4 HTTP/1.1" 200 -
    ImmutableMultiDict([('int', u''), ('3', u''), ('user', u'user')])
    127.0.0.1 - - [23/Dec/2015 20:28:53] "GET /?3&int&user=user HTTP/1.1" 200 -
    """

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

# 请求钩子, 在请求被交给指定的视图处理前，进行处理
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and  \
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

# 管理页面的权限认证
@app.route('/admin')
@login_required
@admin_required # 管理员角色验证
def for_admins_only():
    return 'For administrators!'

# 页面的权限认证
@app.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS) # 其他用户角色认证
def for_moderators_only():
    return 'For comment moderators!'

# 个人主页路由
@app.route('/user/<username>') # 从URL截取用户昵称
def user(username): # 将截取到的昵称做完参数传递给函数 user
    user = User.query.filter_by(username=username).first() # 用获取的昵称在 user 表中查找用户
    if user is None: # 如果没有这个昵称的用户
        abort(404)  # 返回错误页面，404，没有该页面
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    # posts = user.posts.order_by(Post.timestamp.desc()).all() # 用户发布的博客文章列表通过 User.posts 关系获取,User.posts 返回的是查询对象,因此 可在其上调用过滤器
    
    # print user.posts
    '''
SELECT posts.id AS posts_id, posts.body AS posts_body, posts.timestamp AS posts_timestamp, posts.author_id AS posts_author_id
FROM posts
WHERE :param_1 = posts.author_id
    '''
    return render_template('user.html', user=user, posts=posts, pagination=pagination)
    # return render_template('user.html', user=user, posts=posts) # 如果有对应的用户，返回该用户的个人主页

# 个人主页编辑页面
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('user', username=current_user.username)) # 提交后，转到个人主页，显示编辑结果
    # 如果是 GET，或 验证器不通过，显示目前的资料内容
    form.name.data = current_user.name 
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

# 管理员的编辑页面
@app.route('/edit_profile/<int:id>', methods=['GET', 'POST']) # 接受整型的参数，默认是字符串。user 表的 id 列
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id) # 通过 id 获取 对应的 User 条目，如果有，返回对象，没有，返回 404 错误
    form = EditProfileAdminForm(user=user) # 需要传递 user , 用于验证 email 和 username
    if form.validate_on_submit():
        # user 不一定是当前用户
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data) # 通过提交来的 Role 表的主键 id ，从 Role 表 获取角色对象
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('user', username=user.username)) # 提交后，转到个人主页，显示编辑结果
    # 如果是 GET，或 验证器不通过，显示目前的资料内容
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id # 值为 Role.id 列的值，外键
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


# 文章的固定连接
@app.route('/post/<int:id>') # 使用 数据库为文章分配的唯一 id
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

# 文章编辑页面
@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user and not current_user.can(Permission.ADMINISTER): # 如果不是文章作者，也不是管理员。post.author 获取 文章的用户对象。
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('post', id=post.id)) # 进入文章页面, 携带参数 id
    form.body.data = post.body
    return render_template('edit_post.html', form=form, post=post)

# 进行关注
@app.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first() # 查找该用户
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('index'))
    if current_user.is_following(user): # 是否已经关注
        flash('You are already following this user.')
        return redirect(url_for('user', username=username))
    current_user.follow(user) # 进行关注
    flash('You are now following %s' % username)
    return redirect(url_for('user', username=username))

# 取消关注
@app.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('index'))
    if not current_user.is_following(user): # 如果并没有关注
        flash('You are not following this user.')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user) # 取消关注
    flash('You are now unfollow %s' % username)
    return redirect(url_for('user', username=username))

# 粉丝
@app.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int) # 获取要查看的页码
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False) # 对列表分页，将所需页的对象赋值给 pagination
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items] # 从分页对象中获取每个条目对象，并赋值到字典列表

    return render_template('followers.html', user=user, endpoint='followers', pagination=pagination, follows=follows)

# 该用户关注的人
@app.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int) # 获取要查看的页码
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False) # 对列表分页，将所需页的对象赋值给 pagination
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items] # 从分页对象中获取每个条目对象，并赋值到字典列表

    return render_template('followers.html', user=user, endpoint='followed_by', pagination=pagination, follows=follows)


