# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect, abort,    session, url_for, request, g, current_app, make_response
# g: 存储登录的用户信息
from . import main

from .. import db

from flask.ext.login import login_user, logout_user, current_user, login_required
from ..models import User, Post, Role, Comment

from .forms import  EditProfileForm, EditProfileAdminForm, PostForm, CommentForm

# 角色验证
from ..decorators import admin_required, permission_required
from ..models import Permission

from flask.ext.sqlalchemy import get_debug_queries # 记录对数据库的查询信息

# 管理页面的权限认证
@main.route('/admin')
@login_required
@admin_required # 管理员角色验证
def for_admins_only():
    return 'For administrators!'

# 页面的权限认证
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS) # 其他用户角色认证
def for_moderators_only():
    return 'For comment moderators!'

# 个人主页路由
@main.route('/user/<username>') # 从URL截取用户昵称
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
@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username)) # 提交后，转到个人主页，显示编辑结果
    # 如果是 GET，或 验证器不通过，显示目前的资料内容
    form.name.data = current_user.name 
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

# 管理员的编辑页面
@main.route('/edit_profile/<int:id>', methods=['GET', 'POST']) # 接受整型的参数，默认是字符串。user 表的 id 列
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
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=user.username)) # 提交后，转到个人主页，显示编辑结果
    # 如果是 GET，或 验证器不通过，显示目前的资料内容
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id # 值为 Role.id 列的值，外键
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

# 首页
@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit(): # 如果有写的权限，而且提交的表单有效
        # 新文章对象的 author 属性值为表达式 current_user._get_current_object()。
        # current_user 由 Flask-Login 提供,和所有上下文变量一样,也是通过线程内的代理对象实现。 ？？
        # 这个对象的表现类似用户对象,但实际上却是一个轻度包装,包含真正的用户对象。 ？？
        # 数据库需要真正的用户对象,因此要调用 _get_current_object() 方法获取。
        post = Post(body=form.body.data, author=current_user._get_current_object()) # 为提交的文章 新建一个 Post 对象，
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    # 渲染的页数从请求的查询字符串(request.args)中获取,如果没有明确指定,则默认渲染第一页。
    # 参数 type=int 保证参数无法转换成整数时,返回默认值。
    page = request.args.get('page', 1, type=int)
    # print page
    # 1

    # print request
    # <Request 'http://127.0.0.1:5000/' [GET]>

    # print request.args
    # http://127.0.0.1:5000/?2 第二页

    show_followed = False # 默认设置显示所有人的文章

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', '')) # 通过 cookie 中的 show_followed 判断用户意图
    if show_followed: # 如果要求显示关注的人的文章
        query = current_user.followed_posts
    else: # 否则
        query = Post.query # 使用顶级查询，显示所有用户的文章

    # 为了显示某页中的记录,要把 all() 换成 Flask-SQLAlchemy 提供的 paginate() 方法。
    # paginate() 方法的第一个参数是 第几页,也是唯一必需的参数。
    # 可选参数 per_page 用来指定 每页显示的记录数量;如果没有指定,则默认显示 20 个记录。
    # 可选参数 error_ out,当其设为 True 时(默认值),如果请求的页数超出了范围,则会返回 404 错误;如果 设为 False,页数超出范围时会返回一个空列表。
    
    # 为了能够很便利地配置每页显示的记录 数量,参数 per_page 的值从程序的环境变量 FLASKY_POSTS_PER_PAGE 中读取。
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)  # 用上面的 query 替代 Post.query

    # print pagination
    # <flask_sqlalchemy.Pagination object at 0x1041dd790>

    posts = pagination.items
    
    # print posts
    # [<Post u'Nam nulla. Curabitur in libero ut massa volutpat convallis. Nullam sit amet turpis elementum ligula vehicula consequat.'>, <Post u'Duis bibendum, felis sed interdum venenatis, turpis enim blandit mi, in porttitor pede justo eu massa. Donec dapibus.'>]
    
    # posts = Post.query.order_by(Post.timestamp.desc()).all() # 文章列表按照时间戳进行降序排列。

    return render_template('main/index.html', form=form, show_followed=show_followed, posts=posts, pagination=pagination)
    # return "Hello, World!"

    """
    print request.args

ImmutableMultiDict([])
127.0.0.1 - - [28/Dec/2015 22:30:45] "GET / HTTP/1.1" 200 -
ImmutableMultiDict([('page', u'2')])
127.0.0.1 - - [28/Dec/2015 22:30:48] "GET /index?page=2 HTTP/1.1" 200 -
ImmutableMultiDict([('page', u'3')])
127.0.0.1 - - [28/Dec/2015 22:30:58] "GET /index?page=3 HTTP/1.1" 200 -

    """

# 文章的固定连接
@main.route('/post/<int:id>', methods=['GET', 'POST']) # 使用 数据库为文章分配的唯一 id
def post(id):
    post = Post.query.get_or_404(id)

    form = CommentForm()
    if current_user.can(Permission.COMMENT) and form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user._get_current_object(),  post=post) # 通过 relationship 创建的属性，在关系两边进行添加
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1)) # -1，因为最新添加的在post.comments列表的最后，如果想要显示最新的消息，默认显示最后一页
    page = request.args.get('page', 1, type=int)
    # if page == -1:
    #     page = post.comments.count() / current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1 # 直接显示有最新评论的那一页
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)  # 时间，从新到旧

    # print pagination
    # <flask_sqlalchemy.Pagination object at 0x1041dd790>

    comments = pagination.items

    return render_template('post.html', posts=[post], endpoint='.post', form=form, comments=comments, pagination=pagination)
 

# 文章编辑页面
@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user and not current_user.can(Permission.ADMINISTER): # 如果不是文章作者，也不是管理员。post.author 获取 文章的用户对象。
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id)) # 进入文章页面, 携带参数 id
    form.body.data = post.body
    return render_template('edit_post.html', form=form, post=post)


# 进行关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first() # 查找该用户
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user): # 是否已经关注
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user) # 进行关注
    flash('You are now following %s' % username)
    return redirect(url_for('.user', username=username))

# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user): # 如果并没有关注
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user) # 取消关注
    flash('You are now unfollow %s' % username)
    return redirect(url_for('.user', username=username))

# 粉丝
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int) # 获取要查看的页码
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False) # 对列表分页，将所需页的对象赋值给 pagination
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items] # 从分页对象中获取每个条目对象，并赋值到字典列表

    return render_template('followers.html', user=user, endpoint='.followers', pagination=pagination, follows=follows)

# 该用户关注的人
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int) # 获取要查看的页码
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False) # 对列表分页，将所需页的对象赋值给 pagination
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items] # 从分页对象中获取每个条目对象，并赋值到字典列表

    return render_template('followers.html', user=user, endpoint='.followed_by', pagination=pagination, follows=follows)


# 设置 cookie 为 查看所有用户文章
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index'))) # 创建一个重定向到首页的响应
    resp.set_cookie('show_followed', '', max_age=30*24*60*60) # 要求客户端设置 cookie ，键值对 'show_followed':'' , 过期时间，单位 s。默认浏览器关闭后过期
    return resp # 返回响应

# 设置 cookie 为 查看 关注的人的文章
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

# 管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)

    comments = pagination.items

    return render_template('moderate.html', endpoint='.moderate', comments=comments, pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page = request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    print Comment.query.get_or_404(id).disabled
    return redirect(url_for('.moderate', page = request.args.get('page', 1, type=int)))

@main.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if comment is None:
        flash('Invalid comment.')
    elif current_user == comment.author:
        db.session.delete(comment)
        flash('This comment has been delete.')
    else:
        flash("You can not delete this comment.")
    return redirect(url_for('.post', id=comment.post.id))

# 请求钩子, 在请求被交给指定的视图处理前，进行处理
@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        # print request.endpoint
        if not current_user.confirmed and \
        request.endpoint[0:12] != 'auth.confirm' and request.endpoint[0:11] != 'auth.logout' and request.endpoint[0:10] != 'main.index':
    #对于已经登录、没有确认、请求的页面不是令牌页面的 请求
        # return redirect(url_for('unconfirmed'))
        # print request.endpoint[0:6] is 'logout'
            return render_template('auth/unconfirmed.html')
        # 重定向到 未确认页面

# 关闭服务器的路由，测试用
@main.route('/shutdown')
def server():
    if not current_app.testing: # 如果程序没有运行在测试环境，该路由不可用。？？
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown') # 调用 werkzeug 提供的关闭函数关闭服务器
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

"""
记录操作时间大于阈值的数据库操作
"""
# 在视图函数处理完请求后，接受响应对象，进行必要处理，并输出响应对象
# @main.after_app_request
# def after_request(response):
#     for query in get_debug_queries(): # 请求中执行的查询的列表
#         # print query
#         if query.duration >= current_app.config['FLASKY_DB_QUERY_TIMEOUT']:
#             current_app.logger.warning(
#                 'Slow query: %s\nParameters: %s\nDuration: %s\nContext: %s\n' %
#                 (query.statement, query.parameters, query.duration, query.context))
#             # print 'Slow query: %s\nParameters: %s\nDuration: %s\nContext: %s\n' % (query.statement, query.parameters, query.duration, query.context)
#     return response
"""
<query statement="SELECT users.id AS users_id, users.username AS users_username, users.email AS users_email, users.password_hash AS users_password_hash, users.confirmed AS users_confirmed, users.name AS users_name, users.location AS users_location, users.about_me AS users_about_me, users.member_since AS users_member_since, users.last_seen AS users_last_seen, users.avatar_hash AS users_avatar_hash, users.role_id AS users_role_id
FROM users
WHERE users.id = ?" parameters=(2,) duration=0.000>
<query statement="UPDATE users SET last_seen=? WHERE users.id = ?" parameters=('2016-01-08 01:21:47.539851', 2) duration=0.001>

--------------------------------------------------------------------------------
WARNING in views [/Users/chao/Desktop/projects/flask/flask_blog/app/main/views.py:374]:
Slow query: UPDATE users SET last_seen=? WHERE users.id = ?
Parameters: ('2016-01-08 01:23:28.800573', 2)
Duration: 0.000900983810425
Context: /Users/chao/Desktop/projects/flask/flask_blog/app/models.py:120 (can)

--------------------------------------------------------------------------------
Slow query: UPDATE users SET last_seen=? WHERE users.id = ?
Parameters: ('2016-01-08 01:23:28.800573', 2)
Duration: 0.000900983810425
Context: /Users/chao/Desktop/projects/flask/flask_blog/app/models.py:120 (can)

--------------------------------------------------------------------------------
"""

