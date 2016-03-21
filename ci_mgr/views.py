# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import json
import logging
from django.views.decorators.csrf import csrf_exempt

import public
import utils
from django.shortcuts import render, redirect

from exception_mgr.utils import catch_exception_http
import models
import time
import datetime

@catch_exception_http
#@public.auth_user
@csrf_exempt
def build_job(request):
    if request.method == "POST":
        j = utils.Jenkins()
        data = json.loads(request.body)
        job_name = data.get("job_name")
        parameters = {"parameters": data.get("parameters")}
        ret = j.build_job(job_name, parameters)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("POST Only!")

@catch_exception_http
#@public.auth_user
def disable_job(request):
    job_name = request.GET.get("job_name")
    j = utils.Jenkins()
    j.disable_job(job_name)
    return public.success_result_http()

@catch_exception_http
#@public.auth_user
def enable_job(request):
    job_name = request.GET.get("job_name")
    j = utils.Jenkins()
    j.enable_job(job_name)
    return public.success_result_http()

@csrf_exempt
def get_views_view(request):
    j = utils.Jenkins()
    #ret = j.get_views()
    #ret = j.get_view_jobs("agile")
    #ret = j.get_all()
    #view_name = request.GET.get("view_name")
    #ret = j.create_view(view_name)
    data = json.loads(request.body)
    ret = j.create_view_job(data)
    #ret = j.disable_job("ci_test")
    #ret = j.enable_job("ci_test")
    #ret = j.delete_job("ci_test")
    #ret = j.build_job("ci_test")
    #ret = j.get_job_config("ci_test")
    #ret = j.auth
    #ret = j.build_job("ci_test1", {"parameters": [{"name":"branch_num", "value":"trunk"}, {"name":"usermail", "value":"liliurd"},\
    #                              {"name":"daily", "value":""}, {"name":"version", "value":""}]})
    return public.success_result_http(ret)

def report_result(request):
    utils.save_report_result(request)
    return public.success_result_http()

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_module_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ret = utils.save_module(data)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_module_view(request):
    name = request.GET.get("name")
    id = request.GET.get("id")
    ret = {}
    if name:
        ret = utils.get_module_by_name(name)
    elif id:
        ret = utils.get_module_by_id(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def get_module_list_view(request):
    ret = utils.get_module_list()
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_task_view(request):
    if request.method == "POST":
        ret = utils.save_task(request)
        if ret:
            public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_task_view(request):
    id = request.GET.get("id")
    ret = utils.get_task(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def get_task_list_view(request):
    module_id = request.GET.get("module_id")
    ret = utils.get_task_list(module_id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_sub_task_view(request):
    if request.method == "POST":
        ret = utils.save_sub_task(request)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
@csrf_exempt
def set_sub_task_order_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        utils.set_sub_task_order(data)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_sub_task_view(request):
    task_id = request.GET.get("task_id")
    ret = utils.get_sub_task_list(task_id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def get_sub_task_info_view(request):
    id = request.GET.get("id")
    ret = utils.get_sub_task_info(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def bin_sub_task_job_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sub_task_id = data.get("sub_task_id")
        job_id_list = data.get("job_id_list")
        ret = utils.bind_sub_task_job(sub_task_id, job_id_list)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
@csrf_exempt
def set_sub_task_job_order_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ret = utils.set_sub_task_job_order(data)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_sub_task_job_list_view(request):
    sub_task_id = request.GET.get("sub_task_id")
    ret = utils.get_sub_task_job_list(sub_task_id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_module_job_view(request):
    if request.method == "POST":
        ret = utils.save_module_job(request)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_module_job_list_view(request):
    module_id = request.GET.get("module_id")
    ret = utils.get_module_job_list(module_id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def get_module_job_view(request):
    id = request.GET.get("id")
    ret = utils.get_module_job(id)
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def merge_task_record_view(request):
    data = {}
    data["task_id"] = request.GET.get("task_id")
    data["page_current"] = request.GET.get("page_current")
    ret = utils.merge_task_record(data)
    return public.success_result_http(ret)

@catch_exception_http
@csrf_exempt
def start_task_view(request):
    if request.method == "POST":
        ret = utils.start_task(request)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http(ret)
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_task_status_view(request):
    task_id = request.GET.get("task_id")
    ret = utils.get_task_status(task_id)
    return public.success_result_http(ret)

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
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
@csrf_exempt
def rm_sub_task_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data.get("id")
        ret = utils.rm_sub_task(id)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
@csrf_exempt
def rm_task_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data.get("id")
        ret = utils.rm_task(id)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def static_dashboard_view(request):
    ret = utils.static_dashboard()
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
@csrf_exempt
def save_job_reason_view(request):
    if request.method == "POST":
        utils.save_job_reason(request)
        return public.success_result_http()
    else:
        return public.fail_result_http("Only POST!")

@catch_exception_http
@public.auth_user
def get_fail_type_view(request):
    ret = utils.get_fail_type(request.GET.get("id"))
    return public.success_result_http(ret)

@catch_exception_http
@public.auth_user
def manual_task_config_view(request):
    ret = utils.manual_task_config(request.GET.get("task_id"))
    return public.success_result_http(ret)



