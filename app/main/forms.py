# -*- coding:utf-8 -*-
from flask.ext.wtf import Form # 表单类，从第三方扩展的命名空间 导入
from flask.ext.pagedown.fields import PageDownField # 与 TextAreaField 接口一致

from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField, SelectField # 字段类
from wtforms.validators import DataRequired, Required, Length, Email  , Regexp, EqualTo # 验证器，直接从 wtforms.validators 导入
from wtforms import ValidationError
from ..models import User, Role
from . import main

from flask.ext.login import login_required

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

# 首页的 邮件编写 表单
class PostForm(Form):
    body = PageDownField("What's you want to say?", validators=[Required()]) # 启用 markdown，非空。用于写博客
    submit = SubmitField('Submit')

# 评论表单
class CommentForm(Form):
    body = PageDownField("Enter your comment", validators=[Required()]) # 启用 markdown，非空。用于写博客
    submit = SubmitField('Submit')

