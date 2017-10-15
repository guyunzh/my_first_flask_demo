#-*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import Required #用来验证输入信息的

class NameForm(FlaskForm):
    '''
        定义了两个字段，用来输入用户名，还有提交字段
    '''
    name=StringField('What is your name?',validators=[Required()])
    submit=SubmitField('Submit')
