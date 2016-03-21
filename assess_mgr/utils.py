# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''
import json
from django.forms.models import model_to_dict
from django.conf import settings

import models
import public
from web_mgr import utils as web_utlis

def save_module(data):
    m = models.Module(**data)
    m.save()

def get_module(id=None):
    return public.get_model(models.Module, id)

def get_module_api(module_id):
    apis = models.Api.objects.filter(module_id=module_id)
    return public.model_to_list(apis)

def save_scene(data):
    m = models.Scene(**data)
    m.save()

def rm_scene(id):
    models.ApiScene.objects.filter(scene_id=id).delete()
    models.SceneRecord.objects.filter(scene_id=id).delete()
    models.Scene.objects.filter(id=id).delete()

def get_scene(id=None):
    return public.get_model(models.Scene, id)

def save_resource(data):
    m = models.Resource(**data)
    m.save()

def rm_resource(id):
    models.ApiResource.objects.filter(resource_id=id).delete()
    models.Resource.objects.filter(id=id).delete()

def get_resource(id=None):
    return public.get_model(models.Resource, id)

def save_api(data):
    res_list = data.get("resource_list", [])
    if "resource_list" in data:
        del data["resource_list"]
    if "id" in data and not data.get("id"):
        del data["id"]
    m = models.Api(**data)
    m.save()
    tmp = {}
    tmp["api_id"] = m.id
    tmp["resource_list"] = res_list
    save_api_resource(tmp)

def get_api(id=None):
    return public.get_model(models.Api, id)

def rm_api(id):
    models.ApiResource.objects.filter(api_id=id).delete()
    models.ApiScene.objects.filter(api_id=id).delete()
    models.Api.objects.filter(id=id).delete()

def get_scene_api(module_id, scene_id):
    data = models.ApiScene.objects.filter(module_id=module_id, scene_id=scene_id)
    ret = public.model_to_list(data)
    return ret

def save_api_resource(data):
    api_id = data["api_id"]
    resource_list = data["resource_list"]

    models.ApiResource.objects.filter(api_id=api_id).delete()
    for resource in resource_list:
        threshold = resource.get("threshold")
        if threshold:
            models.ApiResource(api_id=api_id, resource_id=resource.get("id"), threshold=threshold).save()
        else:
            models.ApiResource(api_id=api_id, resource_id=resource.get("id"), threshold=0).save()

def get_api_resource(api_id):
    resource = models.ApiResource.objects.filter(api_id=api_id)
    ret = {}
    ret["api_id"] = api_id
    ret["resource_id"] = []
    ret["resource_list"] = []
    for r in resource:
        ret["resource_id"].append(r.resource_id)
        ret["resource_list"].append(model_to_dict(r))
    return ret

def save_scene_record(data):
    data["data"] = json.dumps(data.get("data")) if data.get("data") else "{}"
    if data.get('id'):
        m = models.SceneRecord.objects.filter(id=data.get('id')).update(**data)
        return m
    else:
        m = models.SceneRecord(**data)
        m.save()
        return m.id

def get_scene_record(module_id, scene_id):
    records = models.SceneRecord.objects.filter(module_id=module_id, scene_id=scene_id)
    ret = []
    for record in records:
        tmp = model_to_dict(record)
        tmp['update_time'] = public.datetime2str(record.update_time)
        tmp["data"] = json.loads(record.data)
        ret.append(tmp)
    return ret

def bind_api(data):
    module_id = data.get("module_id")
    scene_id = data.get("scene_id")
    api_list = data.get("api_list")
    models.ApiScene.objects.filter(module_id=module_id, scene_id=scene_id).delete()
    for api in api_list:
        ratio = api.get("ratio") if api.get("ratio") else 0
        models.ApiScene(module_id=module_id, scene_id=scene_id, api_id=api["id"], ratio=ratio).save()


def save_formula(data):
    if models.Formula.objects.filter(record_id=data.get('record_id'), resource_id = data.get('resource_id')):
        m = models.Formula.objects.filter(record_id=data.get('record_id'), resource_id = data.get('resource_id')).update(**data)
        return m
    else:
        m = models.Formula(**data)
        m.save()
        return m.id

def get_formula(record_id):
    records = models.Formula.objects.filter(record_id=record_id)
    ret = []
    for record in records:
        tmp = model_to_dict(record)
        ret.append(tmp)
    return ret


def get_resource_by_name(name):
    resource = models.Resource.objects.filter(name=name)
    return model_to_dict(resource[0])


def get_api_by_scene_module(module_id, scene_id):
    ret = []
    for i in models.ApiScene.objects.filter(module_id = module_id, scene_id = scene_id):
         ret.append( get_api(i.api_id) )
    return ret


def get_threshold_by_api_resource(api_id, resource_id):
    all =  models.ApiResource.objects.filter(api_id = api_id, resource_id = resource_id)
    if len(all):
        return all[0].threshold
    else:
        return False

def get_public(request):
    ret = {}
    ret["module_list"] = get_module()
    ret["auth"] = web_utlis.check_auth(public.get_user_mail(request), public.WORK_ASSESS)
    return ret

def get_api_record(api_id):
    return public.model_to_list(models.ApiRecord.objects.filter(api_id = api_id))

def save_api_record(data):
    data["data"] = json.dumps(data.get("data")) if data.get("data") else "{}"
    if data.get('id'):
        m = models.ApiRecord.objects.filter(id=data.get('id')).update(**data)
        return m
    else:
        m = models.ApiRecord(**data)
        m.save()
        return m.id

def delete_api_record(record_id):
    models.ApiRecord.objects.filter(id=record_id).delete()

def get_api_list_html(module_id, scene_id):
    api_list = get_module_api(module_id)
    scene_api = get_scene_api(module_id, scene_id)
    id_list =[]
    ratio_dict = {}
    for scene in scene_api:
        id_list.append(scene["api_id"])
        ratio_dict[scene["api_id"]] = scene["ratio"]
    body = ""
    for api in api_list:
        body += "<tr>"
        body += '<td>%s</td>' % api["name"]
        body += '<td>%s</td>' % api["creator"]
        body += '<td>%s</td>' % api["desc"]
        body += '<td style="width:52px"><input type="text" style="width:50px" placeholder="Int" id="ratio_%s" value="%s"></td>' % (api["id"], ratio_dict.get(api["id"], 0))
        if api["id"] in id_list:
            body += '<td><input type="checkbox" name="cklist" value="%s" checked="checked"></td>' % api["id"]
        else:
            body += '<td><input type="checkbox" name="cklist" value="%s"></td>' % api["id"]
        body += "<tr>"

    ret = u'''<input type="hidden" id="scene_id" value="%s"><table class="table table-striped table-bordered table-hover table-condensed">
        <thead>
        <tr>
          <th>名称</th>
          <th>添加者</th>
          <th>描述</th>
          <th>比例 %%</th>
          <th><input type="checkbox" id="ckall" name="ckall"></th>
        </tr>
        </thead>
        <tbody>%s</tbody></table>
        <script>
        $(function(){
            $("#ckall").click(function() {
                $('input[name="cklist"]').prop("checked",this.checked);
            });
            var cklist = $("input[name='cklist']");
            cklist.click(function(){
                $("#ckall").prop("checked",cklist.length == $("input[name='cklist']:checked").length ? true : false);
            });
        })
        </script>
        ''' % (scene_id, body)
    return ret