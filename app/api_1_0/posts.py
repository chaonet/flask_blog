# -*- coding:utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from .. import db

from ..models import Post, User

from .authentication import auth
from .errors import forbidden

from .decorators import admin_required, permission_required
from ..models import Permission

# GET 请求文章集合的资源
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)

    return jsonify({
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

    # posts = Post.query.all()
    # return jsonify({'posts': [post.to_json() for post in posts] })

# 返回单个博客文章
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES) # 确保用户有写博客的权限
def new_post():
    post = Post.from_json(request.json) # 文章内容，从 JSON 中提取
    post.author = g.current_user # 作者是用户
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}
    # 如果返回的是一个元组，且元组中的元素可以提供额外的信息。
    # 这样的元组必须是 (response, status, headers) 的形式，且至少包含一个元素。 
    # status 值会覆盖状态代码， headers 可以是一个列表或字典，作为额外的消息标头值。
    # 返回 201 状态码，并在响应头部中包含新建的资源 URL

# 对资源的 put 请求
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES) # 是否有写文章的权限
def edit_post(id):
    post = Post.query.get_or_404(id) # 通过 提交的 id，获取数据库中对应的 post 对象
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER): # 如果当前用户不是作者，或者不是管理员
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body) # 从提交的 JSON 获取 'body'的值，如果没有，默认为已有的 post.body
    db.session.add(post)
    return jsonify(post.to_json())

@api.before_request
@auth.login_required # 保护路由，只允许已登陆用户访问。否则，将用户重定向到 登陆页面
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed: # 注册、登陆，但还没确认 的用户
        return forbidden('Unconfirmed account') # 拒绝
