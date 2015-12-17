# -*- coding:utf-8 -*-
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True) # index 为这列创建索引,提升查询效率; unique 不允许出现重复的值
    email = db.Column(db.String(120), index = True, unique = True)
    posts = db.relationship('Post', backref='author', lazy='dynamic') # 在 Post 中插入 author 反向引用

    def __repr__(self):
    	return '<User %r>' % self.username

    def is_authenticated(self):
    	return True

    def is_active(self):
    	return True

    def is_anonymous(self):
    	return False

    def get_id(self):
    	try:
    		return unicode(self.id)
    	except NameError:
    		return str(self.id)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 外键使用 ForeignKey，指向 User 表的 id

	def __repr__(self):
		return '<Post %r>' % self.body