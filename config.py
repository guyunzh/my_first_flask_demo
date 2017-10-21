#-*- coding:utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True    # 可以每次提交完自动提交
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对
    # 象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True #启用传输层安全协议
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'guyunzh@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '19920814zhsb'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'  #邮件主题前缀
    FLASKY_MAIL_SENDER = 'guyunzh@163.com'#发件人邮箱
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or 'guyunzh@gmail.com'
    FLASKY_POSTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):#将函数变成一个静态方法，让类和实例都可以使用这个方法。与@classmethod不同
        pass

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')  # 用于连接数据的数据库

class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}
