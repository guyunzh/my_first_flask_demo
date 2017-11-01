# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User
from wtforms import ValidationError  # 引入wtforms中的错误机制

'''
    BooleanField为复选框，值为True或者False，
    Email验证电子邮件地址
    Length验证输入字符串长度
    required确保字段中有数据
    Regexp使用正则表达式验证输入值
    EqualTo比较两个字段的值，用于密码确认
'''


class LoginForm(FlaskForm):  # 创建登陆表单
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me loggin in')
    submit = SubmitField('Login in')


class RegistrationForm(FlaskForm):  # 注册用户表单
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64),
                                                   Regexp('^[A-Za-z0-9_.]*$', 0, 'Usernames must have only letters,'
                                                                                 'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), Length(1, 64), EqualTo('password2',
                                                                                        message="Passwords must match.")])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')


class ChangePasswordForm(FlaskForm):  # 修改密码表单
    oldpassword = PasswordField('Old Password', validators=[Required()])
    password = PasswordField('New Password', validators=[Required(), Length(1, 64), EqualTo('password2',
                                                                                            message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('ChangePassword')


# 重置密码，忘记密码表单，分为两个，一个是重置的页面，一个是发送邮件确认重置的页面
class PasswordResetRequestForm(FlaskForm):  # 发送邮件确认重置的页面
    email = StringField('Your Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):  # 密码重置的页面
    email = StringField('Your Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required(), Length(1, 64), EqualTo('password2',
                                                                                        message="Passwords must match.")])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Your Password')

    def valide_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):  # 邮箱重置表单
    newemail = StringField('New email', validators=[Required(), Email()])
    password = PasswordField('Your Password', validators=[Required()])
    submit = SubmitField('Update your email')

    def valide_newmail(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This Email already registered')


class ChangeUsernameForm(FlaskForm):  # 更改用户名
    username = StringField('New name', validators=[Required(), Length(1, 64),
                                                   Regexp('^[A-Za-z0-9_.]*$', 0, 'Usernames must have only letters,'
                                                                                 'numbers, dots or underscores')])
    password = PasswordField('Your Password', validators=[Required()])
    submit = SubmitField('Update your name')

    def valide_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')
