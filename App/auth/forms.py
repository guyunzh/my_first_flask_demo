#-*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from ..models import User
from wtforms import ValidationError  #引入wtforms中的错误机制
'''
    BooleanField为复选框，值为True或者False，
    Email验证电子邮件地址
    Length验证输入字符串长度
    required确保字段中有数据
    Regexp使用正则表达式验证输入值
    EqualTo比较两个字段的值，用于密码确认
'''
class LoginForm(FlaskForm):         #创建登陆表单
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[Required()])
    remember_me=BooleanField('Keep me loggin in')
    submit=SubmitField('Login in')

class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    username=StringField('Username',validators=[Required(),Length(1,64),
                        Regexp('^[A-Za-z0-9_.]*$',0,'Usernames must have only letters,'
                                 'numbers, dots or underscores')])
    password=PasswordField('Password',validators=[Required(),Length(1,64),EqualTo('password2',
                        message="Passwords must match.")])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')