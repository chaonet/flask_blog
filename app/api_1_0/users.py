# -*- coding:utf-8 -*-
from flask import jsonify, request, current_app, url_for
from . import api
from .. import db

from ..models import User, Post

from .authentication import auth
from .errors import forbidden

from .decorators import admin_required, permission_required
from ..models import Permission

@api.route('/users/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/posts/')
@auth.login_required
def get_user_posts(id):
    user = User.query.get_or_404(id)

    page = request.args.get('page', 1, type=int)
    pagination = user.posts.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1, _external=True)

    return jsonify({
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

@api.route('/users/<int:id>/timeline/')
@auth.login_required
def get_user_followed(id):
    user = User.query.get_or_404(id)

    query = user.followed_posts

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed', id=id, page=page+1, _external=True)

    return jsonify({
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        })
