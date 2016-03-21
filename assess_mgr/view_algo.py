
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
import public
import utils
import algo

# yecheng
@csrf_exempt
def set_algo_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"POST only")

    data = json.loads(request.body)
    x = data.get("x")
    y = data.get("y")
    module = data.get("module_id")
    scene = data.get("scene_id")
    resource_name = data.get("resource")
    if len(utils.get_resource_by_name(resource_name)):
        resource_id = utils.get_resource_by_name(resource_name).get('id')
    else:
        print 'get resource id failed'

    record_id = data.get("id")
    if not (x and y and module and scene):
        return public.fail_result_http(u"module, scence, X, Y should not be NONE")

    ret = algo.set_algo_info(module, scene , resource_name, x, y)

    # save formula info
    tmp = {}
    tmp['a'] = ret.get('a')
    tmp['b'] = ret.get('b')

    this_formula = {}
    this_formula['resource_id'] = resource_id if resource_id else 0
    this_formula['record_id'] = record_id
    this_formula['formula'] = json.dumps(tmp)
    utils.save_formula(this_formula)

    if type(ret) == type(""):
        return public.fail_result_http(ret)
    return public.success_result_http(ret)




@csrf_exempt
@public.auth_user
def train_algorithm(request):
    module_id = request.GET.get('module_id')
    scene_id = request.GET.get('scene_id')
    limit  = request.GET.get('limit')

    if scene_id and module_id:
        tmp = utils.get_scene_record(module_id,scene_id)
        for i in tmp:
            i['data_length'] = range(len(i['data'][i['data'].keys()[0]]))
            i['resources'] = []
            i['apis'] = []
            i['api_info'] = []
            api_dict = {}
            for k in i['data'].keys():
                if k != 'total' and k.find('#api#') != 0:
                    i['resources'].append(k)
                if k != 'total' and k.find('#api#') == 0:
                    api_dict[k[5:]] = i['data'][k]
                    #this_api_id = utils.get_api_by_name(k[5:])
                    i['api_info'].append(k) # TODO

            for j in i['data_length']:
                current_api_dict = {}
                for k,v  in api_dict.iteritems():
                    current_api_dict[k] = v[j]
                i['apis'].append(current_api_dict)
        if limit and int(limit) > 0:
            ret = {'scene_records' : tmp[:int(limit)]}
        else:
            ret = {'scene_records': tmp}

        ret['module_id'] = module_id
        ret['scene_id'] = scene_id
        scene_api = utils.get_scene_api(module_id, scene_id)

        for s in scene_api:
            s['api_info'] = utils.get_api(s.get('api_id'))
            # ge threhold
            if s['api_info']:
                s['api_info']['threholds'] = utils.get_api_resource(s.get('api_id'))
                for th in s['api_info']['threholds'].get('resource_list'):
                    th['name'] = utils.get_resource(th.get('resource_id')).get('name')

        ret['scene_info'] = utils.get_scene(scene_id)
        ret['module_info'] = utils.get_module(module_id)
        ret['scene_api'] = scene_api
        ret['all_resource'] = []

        all_resource_ids = []
        # get all resource need
        for s in scene_api:
            for id in s.get('api_info').get('threholds').get('resource_id'):
                if not id in all_resource_ids:
                    all_resource_ids.append(id)
                    ret['all_resource'].append(utils.get_resource(id))

        ret["public"] = utils.get_public(request)
        return render(request, 'assess/train_algorithm.html', {'data': ret})
    else:
        return render(request, 'error.html')


@csrf_exempt
@public.auth_user
def single_api_view(request):
    ret = {}
    ret['public'] = utils.get_public(request)

    api_id = request.GET.get('api_id')
    records = utils.get_api_record(api_id)
    api_resource = utils.get_api_resource(api_id)
    ret['resource'] = []
    ret['records'] = []
    for i in api_resource['resource_id']:
        ret['resource'].append(utils.get_resource(i))


    ret['records'] = records
    for r in ret['records']:
        r['data'] = json.loads(r['data'])
    ret['api_id'] = api_id
    return render(request, 'assess/api_record.html', {'data':ret })

@csrf_exempt
def delete_scene_record(request):
    algo.delete_scene_record(json.loads(request.body))
    return public.success_result_http()


@csrf_exempt
def get_formula_by_threshold(request):
    if request.method != "POST":
        return public.fail_result_http(u"POST only")

    body = json.loads(request.body)
    record_id = body.get('record_id')
    module_id = body.get('module_id')
    scene_id = body.get('scene_id')
    apis = utils.get_api_by_scene_module(module_id=module_id, scene_id = scene_id)
    all_formulas = utils.get_formula(record_id)
    all_y_for_threshold = {}
    for f in all_formulas:
        a = json.loads(f.get('formula')).get('a')
        b = json.loads(f.get('formula')).get('b')
        resource_id = f.get('resource_id')
        for api in apis: # get  threshold
            this_threshold = utils.get_threshold_by_api_resource(api_id=api.get('id'), resource_id= resource_id)
            resource_name = utils.get_resource(resource_id).get('name')

            if all_y_for_threshold.get(resource_name):
                all_y_for_threshold[resource_name] = min( all_y_for_threshold[resource_name], float(this_threshold)*float(a) + float(b))
            else:
                all_y_for_threshold[resource_name] = float(this_threshold)*float(a) + float(b)

    min_y = None
    min_y_resource = None
    for k,v in all_y_for_threshold.iteritems():
        if min_y == None:
            min_y = all_y_for_threshold.get(k)
            min_y_resource = k
        else:
            if all_y_for_threshold.get(k) < min_y:
                min_y_resource = k
                min_y = all_y_for_threshold.get(k)


    return public.success_result_http({'resource_name': min_y_resource, 'tps': min_y})


@csrf_exempt
def save_single_api_record(request):
    id = utils.save_api_record(json.loads(request.body))
    public_info = utils.get_public(request)
    if public_info.get('auth').get('write') != 1:
        return public.fail_result_http('have no write right')
    else:
        return public.success_result_http({'id': id})


@csrf_exempt
def delete_single_api_record(request):
    data = json.loads(request.body)
    public = utils.get_public(request)
    if public.get('auth').get('write') != 1:
        return public.fail_result_http('have no write right')
    if data.get('id'):
        ret = utils.delete_api_record(data.get('id'))
        return public.success_result_http(ret)
    else:
        return public.fail_result_http('id is empty')