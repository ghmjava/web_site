# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
import public
import utils


from exception_mgr.utils import catch_exception_http

@public.auth_user
@csrf_exempt
def save_module_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        data["creator"] = public.get_user_mail(request)
        ret = utils.save_module(data)
        return public.success_result_http(ret)

@public.auth_user
def get_module_view(request):
    id = request.GET.get("module_id")
    ret = utils.get_module(id)
    return public.success_result_http(ret)

@public.auth_user
def get_scene_view(request):
    id = request.GET.get("id")
    ret = utils.get_scene(id)
    return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_resource_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        body = request.POST
        data = {}
        if body.get("id"):
            data["id"] = body.get("id")
        data["name"] = body.get("name")
        data["desc"] = body.get("desc")
        data["creator"] = public.get_user_mail(request)
        utils.save_resource(data)
        return redirect("/assess_mgr/resource")

@public.auth_user
def get_resource_view(request):
    id = request.GET.get("id")
    ret = utils.get_resource(id)
    return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_api_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        data["creator"] = public.get_user_mail(request)
        ret = utils.save_api(data)
        return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def rm_scene_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        id = data.get("id")
        utils.rm_scene(id)
        return public.success_result_http()

@public.auth_user
@csrf_exempt
def rm_resource_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        id = data.get("id")
        utils.rm_resource(id)
        return public.success_result_http()

@public.auth_user
@csrf_exempt
def rm_api_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        id = data.get("id")
        utils.rm_api(id)
        return public.success_result_http()

@public.auth_user
def get_api_view(request):
    id = request.GET.get("id")
    ret = utils.get_api(id)
    return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_api_resource_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        ret = utils.save_api_resource(data)
        return public.success_result_http(ret)

@public.auth_user
def get_api_resource_view(request):
    api_id = request.GET.get("api_id")
    ret = utils.get_api_resource(api_id)
    return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_scene_record_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        if data.get('id'):
            data['modify_by'] = public.get_user_mail(request)
        else:
            data["creator"] = public.get_user_mail(request)
        ret = utils.save_scene_record(data)
        return public.success_result_http(ret)

@public.auth_user
def get_scene_record_view(request):
    module_id = request.GET.get("module_id")
    scene_id = request.GET.get("scene_id")
    ret = utils.get_scene_record(module_id, scene_id)
    return public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def bind_api_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        ret = utils.bind_api(data)
        return public.success_result_http(ret)

################################################
@public.auth_user
def assess_main_view(request):
    data = {}
    data["public"] = utils.get_public(request)
    return render(request, 'assess/assess_base.html', {"data":data})

@public.auth_user
def module_view(request):
    module_id = request.GET.get("module_id")
    data = {}
    data["module_id"] = module_id
    data["public"] = utils.get_public(request)
    scenes = utils.get_scene()
    data["scene"] = scenes
    for scene in scenes:
        scene_id = scene["id"]
        api_list = utils.get_scene_api(module_id, scene_id)
        scene["api_list"] = []
        for api in api_list:
            api["info"] = utils.get_api(api["api_id"])
            scene["api_list"].append(api)

    return render(request, 'assess/module.html', {"data":data})

@public.auth_user
def module_api_view(request):
    module_id = request.GET.get("module_id")
    data = {}
    data["public"] = utils.get_public(request)
    data["api"] = utils.get_module_api(module_id)

    return render(request, 'assess/module_api.html', {"data":data})

@public.auth_user
def scene_view(request):
    data = {}
    data["public"] = utils.get_public(request)
    data["scene"] = utils.get_scene()
    return render(request, 'assess/scene.html', {"data":data})

@public.auth_user
def resource_view(request):
    data = {}
    data["public"] = utils.get_public(request)
    data["resource"] = utils.get_resource()
    return render(request, 'assess/resource.html', {"data":data})

@public.auth_user
def api_view(request):
    data = {}
    data["public"] = utils.get_public(request)
    data["resource"] = utils.get_resource()
    id = request.GET.get("id")
    if id:
        data["api"] = utils.get_api(id)
        data["resource_list"] = utils.get_api_resource(id)
    return render(request, 'assess/api.html', {"data":data})

@public.auth_user
@csrf_exempt
def post_api_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = {}
        module_id = request.POST.get("module_id")
        data["module_id"] = module_id
        data["name"] = request.POST.get("name")
        data["desc"] = request.POST.get("desc")
        data["creator"] = public.get_user_mail(request)
        if request.POST.get("id"):
            data["id"] = request.POST.get("id")
        utils.save_api(data)
        return redirect("/assess_mgr/module_api?id=" + module_id)

@public.auth_user
@csrf_exempt
def save_scene_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        body = request.POST
        data = {}
        if body.get("id"):
            data["id"] = body.get("id")
        data["name"] = body.get("name")
        data["desc"] = body.get("desc")
        data["creator"] = public.get_user_mail(request)
        utils.save_scene(data)
        return redirect("/assess_mgr/scene")

@public.auth_user
def get_api_list(request):
    module_id = request.GET.get("module_id")
    scene_id = request.GET.get("scene_id")
    ret =utils.get_api_list_html(module_id, scene_id)
    return HttpResponse(ret)



