#-*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from . import db,login_manager
from flask_login import UserMixin       #导入认证用户的一系列支持
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer     #为了生成确认令牌
from flask import current_app

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True,index=True)
    users=db.relationship('User',backref='role',lazy='dynamic')
    #lazy='dynamic'表示不加载记录，但是提供加载记录的查询
    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))#外键
    password_hash =db.Column(db.String(128))
    email=db.Column(db.String(64),unique=True,index=True)
    confirmed=db.Column(db.Boolean,default=False)   #判断用户是否已经确认过了

    def __repr__(self):
        return '<User %r>' % self.username

    @property       #规定了密码不能被读取
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter        #设置密码对应的哈希值，然后存入到数据库中
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):     #验证密码用的
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600):      #用来生成令牌
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):        #用来确认用户账户，判断令牌
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True

    def reset_password(self,token,new_password):        #用来确认用户重置密码，判断令牌
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.password=new_password
        db.session.add(self)
        return True

    def generate_email_reset_token(self,new_email,expiration=3600):#生成修改邮箱令牌
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id,'new_email':new_email})

    def change_email(self,token):           #判断邮箱令牌，确认后修改邮箱，此时注意邮箱是已经激活的
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email=data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


@login_manager.user_loader      #用来回调用户的标识符来确认这个用户身份
def load_user(user_id):
    return User.query.get(int(user_id))
