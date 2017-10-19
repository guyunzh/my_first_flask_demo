#-*- coding:utf-8 -*-
from flask import Blueprint

main=Blueprint('main',__name__)

from . import views,error
from ..models import Permission

@main.app_context_processor     #上下文处理器，让定义的变量在所有模板中全局可访问
def inject_permissions():
    return dict(Permission=Permission)