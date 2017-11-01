#-*- coding:utf-8 -*-
import unittest  #导入unittest模块，测试用
from flask import current_app
from App import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')#引入配置里的testing类，为了专门建立一个测试用的数据库
        self.app_context = self.app.app_context()#激活人工上下文
        self.app_context.push()#将应用程序上下文绑定到当前上下文，也就是激活
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()#关闭应用程序上下文

#上面两个方法函数都是自动在测试开始和结束的时候执行

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
