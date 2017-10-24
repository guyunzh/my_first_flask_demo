#-*- coding:utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
db = SQLAlchemy()
mail=Mail()
moment=Moment()
login_manager = LoginManager()
pagedown=PageDown()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])#导入配置信息的类，类里面包含了需要的配置
    config[config_name].init_app(app)#完成各种扩展的初始化任务
    bootstrap .init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)      #使用pagedown，为了编辑文本格式用的
    login_manager .init_app(app)    #初始化用户认证的实例
    login_manager.session_protection = 'strong'     #提供不同的安全等级
    login_manager.login_view = 'auth.login'         #设置登陆页面的端点

    from .auth import auth as blueprint
    app.register_blueprint(blueprint,url_prefix='/auth')

    from .main import main
    app.register_blueprint(main)

    return app

