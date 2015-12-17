# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Required, Length, Email

# print StringField
# <class 'wtforms.fields.core.StringField'>
# print BooleanField
# <class 'wtforms.fields.core.BooleanField'>
# print DataRequired
# <class 'wtforms.validators.DataRequired'>

class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators=[Required()])
	# username = StringField('What is your name ?', validators=[Required()]) # 验证器列表
	remember_me = BooleanField('remember_me', default=False)
	# print remember_me
	# <UnboundField(BooleanField, ('remember_me',), {'default': False})>
	submit = SubmitField('Log In')