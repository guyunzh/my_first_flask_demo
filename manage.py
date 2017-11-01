# -*- coding:utf-8 -*-
import os
from App import create_app, db
from flask_script import Manager, Shell
from App.models import User, Role, Post
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')  # 创建程序实例
manager = Manager(app)  # 初始化命令行脚本实例
migrate = Migrate(app, db)  # 初始化数据库迁移脚本实例


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)  # 创建一个字典，将需要的参数传入


manager.add_command('shell', Shell(make_context=make_shell_context))  # 注册新命令shell，导入字典参数。即导入对象空间
manager.add_command('db', MigrateCommand)


@manager.command  # 自定义命令的一个装饰器，函数名就是一个命令。将一个命令函数添加到注册表
def test():
    '''Run the unit tests.'''  # 注释信息会显示在帮助里面
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
