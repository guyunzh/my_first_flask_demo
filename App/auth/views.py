#-*- coding:utf-8 -*-
from . import auth
from flask import render_template,redirect,url_for,request,flash
from flask_login import login_user,login_required,logout_user,current_user
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,\
    PasswordResetForm,PasswordResetRequestForm,ChangeEmailForm,ChangeUsernameForm
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

@auth.before_app_request        #before_app_request是一个钩子，每次请求都会调用该视图函数
def before_request():           #用来处理注册但是未邮箱确认的用户所能看到的信息
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] !='auth.'\
                                        and request.endpoint !='static':
            return redirect(url_for('auth.unconfirmed'))
#is_authenticated()记录用户登录状态，登录返回True。
#current_user是指当前用户，如果登录了，表示当前用户的代理。
@auth.route('/unconfirmed')         #注册但是未邮箱确认的用户看到的路由
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
#is_anonymous()标记匿名用户的

@auth.route('/confirm')             #用来重新发送邮件的
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/changepassword',methods=['GET','POST'])#用来修改密码的
@login_required
def changepassword():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Password')
    return render_template('auth/changepassword.html',form=form)

@auth.route('/reset',methods=['GET','POST'])       #用来重置密码第一步的邮箱确认
def reset_password():
    if not current_user.is_anonymous:#这个判断是说如果是已经登录的用户就执行这个return，只有游客才能重置密码
        return redirect(url_for('main.index'))
    form=PasswordResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            token=user.generate_confirmation_token()
            send_email(user.email,'Reset Your Password','auth/email/reset_password',
                       user=user,token=token,next=request.args.get('next'))
            flash('An email with instructions to reset your password has been '
                  'sent to you.')
            return redirect(url_for('auth.login'))
        else:
            flash('you have not registed')
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])#用来重置密码确认的
def reset_request_password(token):
    if not current_user.is_anonymous:#这个判断是说如果是已经登录的用户就执行这个return，只有游客才能重置密码
        return redirect(url_for('main.index'))
    form=PasswordResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Unkown email address')
            return redirect(url_for('auth.reset_password'))
        if user.reset_password(token,form.password.data):
            flash('Your password is reset!')
            return redirect(url_for('auth.login'))
        else:
            redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/change_email',methods=['GET','POST'])
@login_required                                                  #用来修改邮箱发送确认邮箱的
def change_email_request():
    form=ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.query.filter_by(email=form.newemail.data).first():
            flash('This Email already registered!!!')
        elif current_user.verify_password(form.password.data):
            token=current_user.generate_email_reset_token(form.newemail.data)
            send_email(form.newemail.data,'Update Email','auth/email/change_email',
                       user=current_user,token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else :
            flash('Invalid  password.')
    return render_template('auth/change_email.html',form=form)

@auth.route('/change_email/<token>')                            #用来确认邮箱从而更改邮箱
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email has been updated.')
    else :
        flash('Invalid request.')
    return redirect(url_for('main.index'))

@auth.route('/change_username',methods=['GET','POST'])
@login_required
def change_username():
    form=ChangeUsernameForm()
    if form.validate_on_submit():
        if current_user.query.filter_by(username=form.username.data).first() is not None :
            flash('This name has exited!')
        elif current_user.verify_password(form.password.data):
            current_user.username=form.username.data
            db.session.add(current_user)
            flash('Your name has changed!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_username.html', form=form)
