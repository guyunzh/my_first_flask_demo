#-*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField,ValidationError
from wtforms.validators import Required ,Length,Email,Regexp
from ..models import Role,User
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    '''
        定义了两个字段，用来输入用户名，还有提交字段
    '''
    name=StringField('What is your name?',validators=[Required()])
    submit=SubmitField('Submit')

class EditProfileForm(FlaskForm):#用来编辑用户信息资料的
    name=StringField('Real Name',validators=[Length(2,64)])
    location=StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me')
    submit=SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):#管理员的信息管理
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    username=StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z0-9_.]*$',0,'Username'
                                                ' must have only letters,numbers,dots or underscores')])
    confirmed=BooleanField('Confirmed')
    role=SelectField('Role',coerce=int)
    name=StringField('Real name',validators=[Length(0,64)])
    location=StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me')
    submit=SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user

    def validate_email( self , field ):
        if field.data !=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registerde.')

    def validate_username(self,field):
        if field.data !=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exit.')

class PostForm(FlaskForm): #主页的提交表单
    body=PageDownField("What's on your mind?",validators=[Required()])
    submit=SubmitField('Submit')
