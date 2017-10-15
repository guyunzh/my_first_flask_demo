#-*- coding:utf-8 -*-
from . import auth
from flask import render_template,redirect,url_for,request,flash
from flask_login import login_user,login_required,logout_user,current_user
from ..models import User
from .forms import LoginForm,RegistrationForm
from .. import db
from ..email import send_email

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)          #用来管理用户的认证状态
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password!!!')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required     #如果你用这个装饰一个视图，它将确保当前的用户是在调用实际视图之前登录和验证。只有登陆的用户才可以访问
def logout():
    logout_user()       #清除cookie，用于登出用户
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])     #用来注册的路由函数
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')         #用来确认用户点击令牌发过来的请求
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else :
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request        #用来处理注册但是未邮箱确认的用户所能看到的信息
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] !='auth.'\
        and request.endpoint !='static':
        return redirect(url_for('auth.unconfirmed'))
#is_authenticated()记录用户登录状态，登录返回True。
#current_user是指当前用户，如果登录了，表示当前用户的代理。如果没登录，表示匿名用户
@auth.route('/unconfirmed')         #注册但是未邮箱确认的用户看到的路由
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
#is_anonymous()标记匿名用户的，登录了，返回False。否则是True

@auth.route('/confirm')             #用来重新发送邮件的
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
