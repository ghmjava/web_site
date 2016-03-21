# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import public
import utils

from exception_mgr.utils import catch_exception_http

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_job_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        data["user"] = public.get_user_mail(request)
        ret = utils.save_job(data)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("POST Only!")

@catch_exception_http
@public.auth_user
def get_job_view(request):
    id = request.GET.get("id")
    ret = utils.get_job(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def get_job_all_view(request):
    ret = utils.get_job_all()
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def set_next_job_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ret = utils.set_next_job(data)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("POST Only!")

@catch_exception_http
@public.auth_user
@csrf_exempt
def rm_job_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data.get("id")
        ret = utils.rm_job(id)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("POST Only!")

@catch_exception_http
@public.auth_user
def get_pre_list_view(request):
    id = request.GET.get("id")
    ret = utils.get_pre_list(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def static_job_view(request):
    ret = utils.static_job()
    return public.success_result_http(ret)

@catch_exception_http
def auto_check_job_status_view(request):
    utils.auto_check_job_status()
    return HttpResponse("")
