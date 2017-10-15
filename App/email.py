#-*- coding:utf-8 -*-
'''
    这个里面是创建发邮件线程的一个地方，为了防止发邮件的时候的等待
'''
from threading import Thread
from flask import current_app,render_template
from flask_mail import Message
from . import mail

def send_async_email(app,msg):
    with app.app_context():#使用app_context()来激活上下文，因为程序上下文都是在一个线程中的，如果在多线程里需要手动激活
        mail.send(msg)

def send_email(to,subject,template,**kwargs):
    app=current_app._get_current_object()#大概意思就是返回当前实例对象，current_app表示当前激活程序的程序实例
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+' '+subject,
                sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr