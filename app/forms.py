# -*- coding:utf-8 -*-
from flask.ext.wtf import Form # 表单类，从第三方扩展的命名空间 导入
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField, SelectField # 字段类
from wtforms.validators import DataRequired, Required, Length, Email  , Regexp, EqualTo # 验证器，直接从 wtforms.validators 导入
from wtforms import ValidationError
from .models import User, Role

# print StringField
# <class 'wtforms.fields.core.StringField'>
# print BooleanField
# <class 'wtforms.fields.core.BooleanField'>
# print DataRequired
# <class 'wtforms.validators.DataRequired'>

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

# 普通用户的资料编辑表单
class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)]) # 因为是可选，允许长度为0
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me') # 文本区域，可以多行，可以拉动
    submit = SubmitField('Submit')

# 管理员的资料编辑表单
class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email(), ])
    username = StringField('Username', validators=[Required(), Length(1, 16), 
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'usernames must have only letters, unmbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    # WTForms 使用 SelectField 对 HTML 表单控件 <select> 进行包装,从而实现下拉列表,用来在这个表单中选择用户角色
    # SelectField 实例 必须在其 choices 属性中设置各选项。
    # 选项必须是一个由元组组成的列表,各元组都包含两个元素:选项的标识符和显示在控件中 的文本字符串。
    # 元组中的标识符是角色的 id,因为这是个整数,所以在 SelectField 中添加 coerce=int 参数,从而把字段的值转换为整数, 而不使用默认的字符串。
    role = SelectField('Role', coerce=int) # 值是 role 的 id
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    # 表单的构造函数，接受 用户对象 作为参数，并保存到实例属性中，在验证时调用
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # choices 列表在表单的构造函数中设定,其值从 Role 模型中获取,使用一 个查询按照角色名的字母顺序排列所有角色。
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()] # 列表推导式
        # [(2, u'Administrator'), (1, u'Moderator'), (3, u'User')]
        self.user = user

    # 检查提交的邮箱
    # 如果字段值没有变化，跳过验证
    # 如果新的与旧的不同，但与其他用户的邮箱重复，报错
    # 如果有变化，且与其他用户不冲突，验证通过
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    # 检查提交的昵称
    # 如果字段值没有变，跳过验证
    # 如果新的与旧的不同，但与其他用户的昵称冲突，报错
    # 如果有变化，且与其他用户不冲突，验证通过
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


