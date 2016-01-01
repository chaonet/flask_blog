# -*- coding:utf-8 -*-
from flask.ext.wtf import Form # 表单类，从第三方扩展的命名空间 导入

from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField, SelectField # 字段类
from wtforms.validators import DataRequired, Required, Length, Email  , Regexp, EqualTo # 验证器，直接从 wtforms.validators 导入

from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()]) # 非空、长度、email 格式
    password = PasswordField('Password', validators=[Required()])
    # username = StringField('What is your name ?', validators=[Required()]) # 验证器列表
    remember_me = BooleanField('remember_me', default=False)
    # print remember_me
    # <UnboundField(BooleanField, ('remember_me',), {'default': False})>
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 16), 
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'usernames must have only letters, unmbers, dots or underscores')])
    # 字母开头，后接最多 63 位 大小写字母、数字、下划线、点
    # 正则表达式、旗帜、验证失败时的错误消息
    email = StringField('Email', validators=[Required(), Length(1, 64), Email(), ])
    password = StringField('password', validators=[Required(), EqualTo('password_con', message='passwords must match.')])
    password_con = StringField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    # 自定义验证函数
    # 如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用
    # 抛出 ValidationError 表示验证失败
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# 修改密码
class Renewpassword(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    new_password = StringField('New password', validators=[Required(), EqualTo('new_password_con', message='passwords must match.')])
    # username = StringField('What is your name ?', validators=[Required()]) # 验证器列表
    new_password_con = StringField('Confirm new password', validators=[Required()])
    # print remember_me
    # <UnboundField(BooleanField, ('remember_me',), {'default': False})>
    submit = SubmitField('Submit')

# 更换邮箱
class Renewmail(Form):
    new_email = StringField('New email', validators=[Required(), Length(1, 64), Email(), ])
    submit = SubmitField('Submit')

# 输入找回密码的邮箱
class Newpassword(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email(), ])
    submit = SubmitField('Submit')

# 输入新密码
class Newpassword_con(Form):
    password = StringField('password', validators=[Required(), EqualTo('password_con', message='passwords must match.')])
    password_con = StringField('Confirm password', validators=[Required()])
    submit = SubmitField('Submit')

