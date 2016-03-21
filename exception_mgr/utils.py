# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import traceback
import functools
from models import SeException
import public
import logging

# 是否开启错误日志记录功能
RECORD_SWITCH = True;

def _record_exception(func, *args, **kwargs):
    """记录错误接口
    parameters:

    func=name    #函数名
    options = "xxxxx"    #函数入参

    """
    if RECORD_SWITCH == True:
        try:
            se_exception = SeException(func_name=func.__name__)
            se_exception.exception = traceback.format_exc()
            options = ""
            request = args[0]
            if request.method == "POST":
                options += repr(request.POST) + ","
            elif request.method == "GET":
                options += repr(request.GET) + ","
            options += repr(args[1:]) + ","
            options += repr(kwargs)
            se_exception.options = options
            se_exception.save()

        except Exception, e:
            print e
    else:
        pass;

# 外部http接口，采用本修饰器
def catch_exception_http(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except:
            _record_exception(func, *args, **kwargs)
            result = public.exception_result_http()
            return result
        finally:
            options = ""
            request = args[0]
            if request.method == "POST":
                options += repr(request.POST) + ","
            elif request.method == "GET":
                options += repr(request.GET) + ","
            options += repr(args[1:])
            if func.__name__ not in public.FUNC_BLACK_MENU:
                logging.info("http call func:%s, args:%s, kwargs:%s, result:%s" \
                             % (func.__name__, options, repr(kwargs), repr(result.content)))
    return decorator

