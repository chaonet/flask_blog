# -*- coding:utf-8 -*-
from flask import jsonify, request, current_app, url_for, g
from . import api
from .. import db

from ..models import User, Post, Comment

from .authentication import auth
from .errors import forbidden

from .decorators import admin_required, permission_required
from ..models import Permission

@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1, _external=True)

    return jsonify({
            'comments': [comment.to_json() for comment in comments],
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT) # 确保用户有评论的权限
def new_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json) # 文章内容，从 JSON 中提取
    comment.author = g.current_user # 作者是用户
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'Location': url_for('api.get_one_comment', id=comment.id, _external=True)}

@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)

    return jsonify({
            'posts': [comment.to_json() for comment in comments],
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

@api.route('/comments/<int:id>')
def get_one_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())

@api.before_request
@auth.login_required # 保护路由，只允许已登陆用户访问。否则，将用户重定向到 登陆页面
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed: # 注册、登陆，但还没确认 的用户
        return forbidden('Unconfirmed account') # 拒绝
