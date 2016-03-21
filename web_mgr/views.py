# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''
import logging
import json
import re
import time
import collections
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
import public
import utils
from data_mgr import utils as data_utils
from data_mgr.value import MODULE_DICT
import datetime
import requests
from job_mgr import utils as job_utils
from ci_mgr import utils as ci_utils

def check_alive(request):
    return HttpResponse("alive")

def redirect_login(request):
    host = request.META.get("HTTP_HOST")
    if request.GET.get("code"):
        utils.set_user_cookie(request)
        redirect_url = request.GET.get("redirect_login")
        if redirect_url:
            url = redirect_url
        else:
            url = "http://" + host
        return redirect(url)

def user_logout_view(request):
    utils.del_user_cookie(request)
    host = request.META.get("HTTP_HOST")
    if host:
        url = "http://" + host
    else:
        url = public.WEB_URL
    return redirect(public.AUTH_URL+url)

@csrf_exempt
@public.auth_user
def home(request):
    data = {}
    if request.GET.get("code"):
        host = request.META.get("HTTP_HOST")
        if host:
            url = "http://" + host
        else:
            url = public.WEB_URL
        return redirect(url)
    if request.method == "GET":
        mob = data_utils.static_mob()
        newlab = data_utils.static_newlab()
        job_record = data_utils.get_latest_job_record_list()
        data = {"MOB": mob, "NEWLAB": newlab, "job_record": job_record}
        return render(request, 'main2.html', {"data": data})

@csrf_exempt
@public.auth_user
def performance_detail_view(request):
    '''数据详情'''
    data = {}
    data["env"] = request.GET.get("env", public.ENV_NEWLAB)
    data["interface"] = request.GET.get("interface", "all")
    data["interface_type"] = request.GET.get("interface_type", "all")
    data["interface_info"] = data_utils.get_interface_info()
    if request.method == "POST":
        data["env"] = request.GET.get("env", public.ENV_NEWLAB)
        data["interface"] = request.POST.get("interface")
        data["interface_type"] = request.POST.get("interface_type")
        data["start"] = request.POST.get("start")
        data["end"] = request.POST.get("end")
    data["detail"] = data_utils.get_dashboard(data, num=100)

    return render(request, 'performance_detail.html', {"data": data})

@csrf_exempt
@public.auth_user
def performance_view(request):
    '''趋势图'''
    data = {}
    data["env"] = request.GET.get("env", public.ENV_NEWLAB)
    data["interface"] = request.GET.get("interface", 1)
    data["interface_info"] = data_utils.get_interface_info()
    if request.method == "POST":
        data["env"] = request.GET.get("env", public.ENV_NEWLAB)
        data["interface"] = request.POST.get("interface")
        data["start"] = request.POST.get("start")
        data["end"] = request.POST.get("end")
    ret = data_utils.get_dashboard_info(data)

    return render(request, 'performance.html', {"data": ret})

@csrf_exempt
@public.auth_user
def mob_detail_view(request):
    '''数据详情'''
    data = {}
    data["env"] = request.GET.get("env", public.ENV_MOB)
    data["type"] = request.GET.get("type", public.TYPE_CPU)
    data["scene"] = request.GET.get("scene", public.SCENE_MONKEY)
    data["start"] = request.GET.get("start")
    data["end"] = request.GET.get("end")
    if request.method == "POST":
        data["env"] = request.POST.get("env", public.ENV_MOB)
        data["type"] = request.POST.get("type")
        data["scene"] = request.POST.get("scene")
        data["start"] = request.POST.get("start")
        data["end"] = request.POST.get("end")
    data["detail"] = data_utils.get_dashboard(data, num=100)

    return render(request, 'mob_detail.html', {"data": data})


@csrf_exempt
@public.auth_user
def mob_view(request):
    '''趋势图'''
    data = {}
    data["env"] = request.GET.get("env", public.ENV_MOB)
    data["type"] = request.GET.get("type", public.TYPE_CPU)
    data["scene"] = request.GET.get("scene", public.SCENE_MONKEY)
    data["start"] = request.GET.get("start")
    data["end"] = request.GET.get("end")
    if request.method == "POST":
        data["env"] = request.POST.get("env", public.ENV_MOB)
        data["type"] = request.POST.get("type")
        data["scene"] = request.POST.get("scene")
        data["start"] = request.POST.get("start")
        data["end"] = request.POST.get("end")
    ret = data_utils.get_dashboard_info(data)

    return render(request, 'mob.html', {"data": ret})


@csrf_exempt
@public.auth_user
def get_interface_view(request):
    tmp = {}
    tmp["interface_type"] = request.GET.get("interface_type", "all")
    if request.method == "POST":
        tmp["interface_type"] = request.POST.get("interface_type")
    data = data_utils.static_newlab(tmp)
    data["interface_type"] = tmp["interface_type"]
    return render(request, 'interface.html', {"data": data})

@csrf_exempt
@public.auth_user
def get_promotion_record_view(request):
    data = {}
    data["promotion"] = request.GET.get("promotion")
    if request.method == "POST":
        data["promotion"] = request.POST.get("promotion")
    ret = {}
    ret["p_id"] = data["promotion"]
    ret["promotion"] = data_utils.get_promotion()
    ret["record"] = data_utils.get_promotion_record(data)
    return render(request, 'promotion.html', {"data": ret})

@csrf_exempt
@public.auth_user
def get_svn_history_view(request):
    data = {}
    data["create"] = request.GET.get("create")
    data["module"] = request.GET.get("module")
    if request.method == "POST":
        data["create"] = request.POST.get("create")
        data["module"] = request.POST.get("module")
    ret = data_utils.get_svn_history_test(data)
    return render(request, 'svn_history.html', {"data": ret})


@csrf_exempt
@public.auth_user
def jenkins_view(request):
    public_date = data_utils.get_public(request)
    group_id = public_date.get('group_id')
    # 默认 newlab
    name = "agile"
    ret = {}
    """
    ret['version'] = data_utils.get_seal_or_newlab_version()
    """
    ret['biz_version'] = data_utils.get_seal_or_newlab_version('biz')
    ret['shanghaife_version'] = data_utils.get_seal_or_newlab_version('shanghaife')

    ret['online'] = []

    ret['data'] = {}
    ret['data']['jobs'] = []

    content = data_utils.get_online_package()

    collection_job = data_utils.get_collection(request)
    job_list = []
    for job in collection_job:
        job_list.append(job.get("id"))
    if int(group_id) == 0:  # others
        group_job = data_utils.get_jobs_not_group()
    elif int(group_id) == -1:
        group_job = collection_job
    else:
        group_job = data_utils.get_group_jobs(group_id)

    for i in group_job:
        if i["id"] in job_list:
            i["collection"] = 1
        if i['name'].startswith("newlabs_"):
            tmp_job_name = i['name']
            i['jobname'] = tmp_job_name
            i['name'] = i['name'][8:]

            # get specific info
            job = data_utils.JenkinsInfo(name=name, job = tmp_job_name)
            if job.get_status() == False:
                continue
            this_ret = job.get_ret()

            if not this_ret.get('lastBuild'):
                this_ret['lastBuild'] = {}

            i['url'] = this_ret.get('url')
            # get seald version info and operator
            this_oper_info = data_utils.get_latest_job_record(i['jobname'])
            i['sealed_version'] = this_oper_info['sealed_version']
            online_info = data_utils.get_latest_online_version(content, i['jobname'])


            if online_info != False:
                i['has_online_version'] = True
                i['online_version'] = online_info

                tmp_dict = {}
                tmp_dict['jobname'] = i['jobname']
                tmp_dict['online_version'] = online_info
                ret['online'].append(tmp_dict)
            else:
                i['has_online_version'] = False

            i['newlab_version'] = this_oper_info['newlab_version']
            i['user'] = this_oper_info['user']

            if this_ret['color'] == 'blue':
                i['lastbuild_status'] = 'success'
            elif this_ret['color'] == 'disabled':
                i['lastbuild_status'] ='disabled'
            elif this_ret['color'] == 'notbuilt':
                i['lastbuild_status'] ='notbuilt'
            elif this_ret['color'].find('anime'):
                i['lastbuild_status'] ='building'
            else:
                i['lastbuild_status'] = 'fail'


            if 'number' in this_ret['lastBuild']:
                i['lastBuild'] = this_ret['lastBuild']['number']
            else:
                i['lastBuild'] = ""

            if 'url' in this_ret['lastBuild']:
                i['lastBuild_console'] = this_ret['lastBuild']['url'] + 'console'
                i['lastBuild_consoleText'] = this_ret['lastBuild']['url'] + 'consoleText'
            else:
                i['lastBuild_console'] = ''
                i['lastBuild_consoleText'] = ''

            i['view'] = name
            i['buildable'] = this_ret['buildable']
            i['trigger_url'] = "http://jenkins.meiliworks.com/view/" + name + "/job/" + tmp_job_name + "/build?delay=0sec"

            if len(this_ret['property']) != 1:
                # 需要参数  目前支持1个参数

                this_param_info = this_ret['property'][1]['parameterDefinitions'][0]
                i['trigger_param'] = this_param_info['name']
                i['trigger_param_description'] = this_param_info['description']
                tmp_default_param = {}
                tmp_default_param[this_param_info["defaultParameterValue"]['name'].encode("utf-8")] = this_param_info["defaultParameterValue"]['value'].encode("utf-8")
                i['trigger_default_param'] = json.dumps(tmp_default_param)
                """
                # 支持多参数
                i['trigger_param'] = []
                i['trigger_param_description'] = []
                i['trigger_default_param'] = []
                this_param_info_array = this_ret['property'][1]['parameterDefinitions']
                for this_param_info in this_param_info_array:
                    i['trigger_param'].append(this_param_info['name'])
                    i['trigger_param_description'].append(this_param_info['description'])
                    tmp_default_param = {}
                    tmp_default_param[this_param_info["defaultParameterValue"]['name'].encode("utf-8")] = this_param_info["defaultParameterValue"]['value'].encode("utf-8")
                    i['trigger_default_param'].append(json.dumps(tmp_default_param))
                """
            else:
                # 不需要参数, 都设成 ‘none’ 供前端判断
                i['trigger_param' ] = 'none'
                i['trigger_default_param'] = 'none'

            # add classification
            ret['data']['jobs'].append(i)


    #获取用户权限信息
    ret["data"]["public"] = public_date
    ret["auth"] = utils.check_auth(public.get_user_mail(request), public.WORK_PRE_LAUNCH)
    return render(request,"jenkinsnew.html", ret)


#liujichao
@csrf_exempt
@public.auth_user
def get_svn_test_view(request):
    data_utils.save_push_status()#存储上线状态数据
    data = {}
    if request.method == "GET":
        data["create"] = request.GET.get("create")
        data["module"] = request.GET.get("module")
        data["user"]=request.POST.get("user")
    if request.method == "POST":
        data["create"] = request.POST.get("create")
        data["module"] = request.POST.get("module")
        data["user"]=request.POST.get("user")
    data_utils.save_goback_information()#存储上线回归状态
    ret=data_utils.get_svn_history_test(data)
    data_report=data_utils.get_auto_report(data)
    data_push=data_utils.get_push_status(data)
    release_plan=data_utils.get_release_plan(data)
    get_goback = data_utils.get_goback_information(data)
    data_utils.get_newlab_jenkinsjob()
    notinplan = []
    a = 1
    for detail in ret["detail"] :
        for plan_module in release_plan:
            if detail["module"] in plan_module["releaseModel"]:
                a = 0
        if a == 1 :
            tem = {}
            tem["module"]=detail['module']
            notinplan.append(tem)
    # get all commit user
    commitUserdict = {}
    for detail in ret['detail']:
        this_module = detail['options']['moduleName']
        commitUserdict[this_module] = []
        for i in detail['options']['svnCommitList']:
            if i['commitUser'] in commitUserdict[this_module]:
                continue
            else:
                commitUserdict[this_module].append(i['commitUser'])

    return render(request, 'svn_test.html', {"data":ret,"commitUserdict":commitUserdict,"data_report":data_report,"data_push":data_push,"notinplan":notinplan,"get_goback":get_goback})

#jichaoliu
def save_Release_Plan(request):
#存储推送来的数据！-Release_plan
    logging.warning(request)
    data={}
    if request.method == "POST":
        data["task_id"] = request.POST.get("task_id")
        data["now_role_cursor"] = request.POST.get("now_role_cursor")
    else:
        data["task_id"] = request.GET.get("task_id")
        data["now_role_cursor"] = request.GET.get("now_role_cursor")

    err = data_utils.save_release_plan(data)
    if err:
        return public.fail_result_http(err, data)
    return public.success_result_http()

#lijichao
@csrf_exempt
def save_package_status(request):
#存储推送来的数据！-package_status

    temp = re.findall('addData_reason.*({.*?})', str(request))
    data ={}
    if request.method == "POST":
        data["addData_reason"] = temp[0]
        err = data_utils.save_package_status(data)
        if err:
            return public.fail_result_http(err, data)
    else:
        data["addData_reason"] = temp[0]
        err = data_utils.save_package_status(data)
        if err:
            return public.fail_result_http(err, data)
        return public.success_result_http()

#lijichao
@csrf_exempt
def save_goback_information(request):
#存储推送来的数据！-package_status
    if request.method == "POST":
        err = data_utils.save_goback_information()
        if err:
            return public.fail_result_http(err)
    else:
        err = data_utils.save_goback_information()
        if err:
            return public.fail_result_http(err)
        return public.success_result_http()


#lijichao  更新数据
def save_information(request):
#存储推送来的数据！-package_status
    data_utils.save_push_status()#存储上线状态数据
    data_utils.save_goback_information()#存储上线回归状态
    return public.success_result_http()



@public.auth_user
@csrf_exempt
def svn_history_only(request):
    module = request.GET.get('module')
    branch = request.GET.get('branch')
    sn = request.GET.get('sn')

    start = branch.split('_')[-2]
    start_time = public.str2datetime(start, "%Y%m%d")
    end_time = start_time + datetime.timedelta(days=1)
    end = public.datetime2str(end_time, "%Y%m%d")

    #start = request.GET.get("start")
    #end = request.GET.get("end")
    import re

    ret = []
    sn_dict = {}
    sn_dict['no_sn'] = []
    if not (module and branch):
        return public.fail_result_http(u"参数错误")
    else:
        tmp_ret = data_utils.get_branch_svn_log(module,branch, start, end)
        #get all sn
        sn_list = []
        for r in tmp_ret:
            tmp = r.get('comment')
            this_sn = tmp[tmp.find('sn=') + 3: tmp.find(';')].strip()
            if this_sn in sn_list:
                continue
            else:
                if re.match('^\d+$',this_sn):
                    sn_list.append(this_sn)
                else:
                    continue
        for r in tmp_ret:
            comment = r.get('comment')
            if comment.find('sn=') != -1:
                sn_no = comment[comment.find('sn=') + 3: comment.find(';')].strip()
                if re.match('^\d+$',sn_no):
                    if sn_dict.has_key(sn_no):
                        sn_dict[sn_no].append(r)
                    else:
                        sn_dict[sn_no] = [r]
            else:
                sn_dict['no_sn'].append(r)


        return render(request, 'commitlist.html',{'data':sn_dict, 'sns': sn_list, })




@csrf_exempt
def timeline(request):
    if request.method != "GET":
        return public.fail_result_http("Only support GET")

    module = request.REQUEST['module']
    job_name = "newlabs_" + module
    print job_name

    # get online info
    content = data_utils.get_online_package()

    if len(content) != 0:
        online_version = data_utils.get_latest_online_version(content, job_name)
    else:
        return "no online version"
    # get ctime of online version
    online_time = data_utils.get_version_ctime(online_version)

    # get last 2 job record
    job_record_list = data_utils.get_job_record_by_type_job_name(job_name,3,2)
    job_record_list.reverse()


    time1 = job_record_list[0]['time']
    time2 = public.datetime2str(online_time)
    #time2 = job_record_list[1]['time']

    # get svn record between time1 and time2
    svn_list = data_utils.get_branch_svn_log(module, "trunk", start=time1, end=time2)


    # get last trigger record
    trigger_record = data_utils.get_job_record_by_type_job_name(job_name,2,1)[0]

    # merge 2 list sort by time

    if svn_list != None:
        for i in svn_list:
            i['time'] = i['time'][:19]
    else:
        svn_list = []

    ret = [job_record_list[0]] + svn_list + [job_record_list[1]]

    # get trunk svn commit after last sealed

    start =  job_record_list[1]['time']
    end = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    after_seal = data_utils.get_branch_svn_log(module, "trunk", start=start, end=end)

    if after_seal != None:
        for j in after_seal:
            j['time'] = j['time'][:19]
    else:
        after_seal = []


    ret.extend(after_seal)

    trigger_record['time'] = trigger_record['time'][:19]
    trigger_record['comment'] = 'publish'

    inserted = False
    for i in range(len(ret)):
        if ret[i]['time'] < trigger_record['time']:
            continue
        else:
            ret.insert(i, trigger_record)
            inserted = True
            break

    if inserted == False:
        ret.append(trigger_record)

    ret.reverse()
    return render(request,'timeline.html', {'data': ret})



@csrf_exempt
def online_info(request):
    name = "agile"
    view = data_utils.JenkinsInfo(name)
    ret = []

    online_info_dict =  data_utils.get_online_info()

    for i in view.get_ret():
        if i['name'].startswith("newlabs_"):
            i['jobname'] = i['name']
            i['name'] = i['name'][8:]
            ###
            if online_info_dict:
                online_info = online_info_dict.get(i['name'].capitalize())
            else:
                online_info = None

            if online_info != None:
                i['has_online_version'] = True
                i['online_version'] = online_info.get('version')

                # get online version svn info
                branch = online_info.get('version')
                start = branch.split('_')[-2]
                start_time = public.str2datetime(start, "%Y%m%d")
                end_time = start_time + datetime.timedelta(days=1)
                end = public.datetime2str(end_time, "%Y%m%d")
                this_svn = data_utils.get_branch_svn_log(i['name'],branch, start, end)

                sn_dict = {}
                sn_dict['no_sn'] = []
                if this_svn:
                    for r in this_svn: # get sn and group by sn
                        comment = r.get('comment')
                        if comment.find('sn=') != -1:
                            sn_no = comment[comment.find('sn=') + 3: comment.find(';')].strip()
                            if re.match('^\d+$',sn_no):
                                if sn_dict.has_key(sn_no):
                                    sn_dict[sn_no].append(r)
                                else:
                                    sn_dict[sn_no] = [r]
                        else:
                            sn_dict['no_sn'].append(r)

                i['svn_info'] = sn_dict
                ret.append(i)
    return render(request, 'online.html', {'data': ret})




# CI


@csrf_exempt
@public.auth_user
def get_task_list_view(request):
    module_name = request.GET.get("module")
    module_id = ci_utils.get_module_by_name(module_name)['id']
    ret = {}
    ret['task'] = ci_utils.get_task_list(module_id)
    for i in ret['task']:
        i['module_name'] = ci_utils.get_module_by_id(i['module_id'])['name']

    ret['module'] = ci_utils.get_module_list()
    ret['current_module'] = {}
    ret['current_module']['name'] = module_name
    ret['current_module']['id'] = module_id
    return render(request, 'ci_mgr/ci_task.html', {"data":ret})


@csrf_exempt
@public.auth_user
def get_task_list_view(request):
    module_name = request.GET.get("module")
    type = request.GET.get("type") # create or modify
    module_id = ci_utils.get_module_by_name(module_name).get('id')
    ret = {}
    ret['task'] = ci_utils.get_task_list(module_id)
    for i in ret['task']:
        i['status'] = ci_utils.get_task_status(i['id'])
        i['module_name'] = ci_utils.get_module_by_id(i['module_id'])['name']
        tmp_subtask = ci_utils.get_sub_task_list(i['id'])
        i['sub_task'] = tmp_subtask['include'] + tmp_subtask['exclude']
    ret['module'] = ci_utils.get_module_list()
    ret['current_module'] = {}
    ret['current_module']['name'] = module_name
    if module_id:
        ret['current_module']['id'] = module_id
    else:
        return render(request, 'ci_mgr/ci_error.html')

    ret['types'] = range(1,5)



    if type == 'create' or type == None:
        return render(request, 'ci_mgr/ci_task.html', {"data":ret})
    elif type == 'modify':

        task_id = request.GET.get("task_id")

        ret['current_task'] = ci_utils.get_task(task_id)

        if ret['current_task'] == {}:
            return render(request, 'ci_mgr/ci_task.html', {"data":ret})
        if ret['current_task']['module_id'] != ret['current_module']['id']:
            ret['module_not_match'] = 1
        else:
            ret['module_not_match'] = 0
        return render(request, 'ci_mgr/ci_task.html', {"data":ret})


@csrf_exempt
@public.auth_user
def sub_task_view(request):
    task_id = request.GET.get("task_id")
    type = request.GET.get("type") # create or modify
    subtask_id = request.GET.get("subtask_id")
    page_current = request.GET.get('page_current')
    if not page_current:
        page_current = 1
    sub_task = ci_utils.get_sub_task_list(task_id)
    ret = {}
    ret['module'] = ci_utils.get_module_list()

    name = "agile"
    view = data_utils.JenkinsInfo(name)
    ret['jenkins_module'] = []

    for i in view.get_ret():
        if i['name'].startswith("newlabs_"):
            this_module = i['name'][8:]
            ret['jenkins_module'].append(this_module)

    ret['current_task'] = ci_utils.get_task(task_id)
    for i in sub_task['include']:
        i['jobs'] = ci_utils.get_sub_task_job_all(i['id'])

    ret['current_task']['sub_task'] = sub_task['include']
    ret['current_task']['sub_task_exclude']  = sub_task['exclude']
    ret['current_task']['sub_task_no_seq'] = []
    ret['current_module'] = {}
    ret['current_module']['id'] = ci_utils.get_module_by_id(ret['current_task']['module_id'])['id']
    module_jobs = ci_utils.get_module_job_list(ret['current_module']['id'])
    ret['module_jobs'] = module_jobs
    ret['current_module']['name'] = ci_utils.get_module_by_id(ret['current_task']['module_id'])['name']
    ret['types'] = range(1,5)

    ret['all_sub_task'] = ci_utils.get_sub_task_all(task_id)
    job_tree = {}
    for i in ret['all_sub_task']:
        job_tree[i['name']] = {}
        job_tree[i['name']]['jobs'] = ci_utils.recursion_scan(ci_utils.get_sub_task_job_list(i['id'])['jobs'])
        job_tree[i['name']]['depth'] = ci_utils.get_sub_task_job_list(i['id'])['deep']
    if type:
        if type == 'modify' and sub_task:
            ret['current_subtask'] = ci_utils.get_sub_task_info(subtask_id)
            return render(request, 'ci_mgr/ci_subtask_config.html', {'data':ret})
        elif type=='create':
            return render(request, 'ci_mgr/ci_subtask_config.html', {'data':ret})


    ret['job_tree'] = {}
    for k,v in job_tree.iteritems():
        ret['job_tree'][k] = {}
        ret['job_tree'][k]['jobs'] = []
        ret['job_tree'][k]['depth'] = job_tree[k]['depth']
        for i in job_tree[k]['jobs']:
            ret['job_tree'][k]['jobs'].append( '[' + json.dumps(i) + ']')

    for t in ret['current_task']['sub_task']:
        t['job_line_cnt'] = len(job_tree[t['name']]['jobs'])
        t['job_depth'] = job_tree[t['name']]['jobs']

    ret['all_depth'] = 0
    ret['row_len'] = 0
    for k,v in job_tree.iteritems():
        ret['all_depth'] = ret['all_depth'] + job_tree[k]['depth']
        for i in ret['current_task']['sub_task']:
            if i['name'] == k:
                i['job_max_depth'] = job_tree[k]['depth']

                i['block_len'] = 100 + 110*i['job_max_depth']
                if i['block_len'] > 300:
                    ret['row_len'] = ret['row_len'] + i['block_len']
                else:
                    ret['row_len'] = ret['row_len'] + 300

    ret['current_task']['sub_task_cnt'] = len(ret['current_task']['sub_task'])
    ret['row_len'] = ret['row_len'] + ret['current_task']['sub_task_cnt']*80

    # 获取运行记录
    task_record = ci_utils.merge_task_record({'task_id':task_id, 'page_current':page_current})
    for task_item in task_record['task']:
        task_item['params_str'] = json.dumps(task_item['params'])
        for sub_task_item in task_item['sub_task']:
            for job_item in sub_task_item['job']:
                job_item['build_url'] = job_item['options'].get('result', {}).get('build_url')
    ret['task_record'] = task_record
    ret['fail_types'] = ci_utils.get_fail_type()
    return render(request, 'ci_mgr/ci_subtask.html', {'data':ret})


@csrf_exempt
@public.auth_user
def module_config_view(request):
    ret = {}
    module = request.GET.get('module')
    if module: # modify a existing module
        ret['current_module'] = ci_utils.get_module_by_name(module)
    ret['module'] = ci_utils.get_module_list()
    ret['types'] = range(4)
    return render(request, 'ci_mgr/ci_module_config.html', {'data' : ret})


@csrf_exempt
@public.auth_user
def jobs_view(request):
    ret = {}
    module_name = request.GET.get('module') # name
    ret['current_module'] =  ci_utils.get_module_by_name(module_name)
    ret['current_task'] = request.GET.get('task_id') # id
    ret['current_subtask'] = request.GET.get('sub_task') # id
    ret['module'] = ci_utils.get_module_list()
    if ret['current_module']:
        ret['tasks'] = ci_utils.get_task_list(ret['current_module']['id'])
    else:
        ret['tasks'] = ci_utils.get_task_all()

    if ret['current_task'] :
        ret['sub_tasks'] = ci_utils.get_sub_task_all(ret['current_task'])
    else:
        ret['sub_tasks'] = ci_utils.get_sub_task_all()

    ret['jobs'] = []

    if ret['current_module']:
        ret['jobs'] = ci_utils.get_module_job_list(ret['current_module']['id'])
    else: # get all module jobs
        for m in ret['module']:
            ret['jobs'].extend(ci_utils.get_module_job_list(m['id']))

    for j in ret['jobs']:
        j['module'] = ci_utils.get_module_by_id(j['module_id'])['name']

    #all_task = ci_utils.get_task_all()

    return render(request, 'ci_mgr/ci_jobs.html', {'data':ret})


@csrf_exempt
@public.auth_user
def job_create_view(request):
    module_id = request.GET.get('module_id')
    ret = {}
    ret['module_id'] = int(module_id)
    ret['module'] = ci_utils.get_module_list()
    ret['types'] = range(4)
    return render(request, 'ci_mgr/ci_job_opr.html', {'data': ret})

@csrf_exempt
@public.auth_user
def job_modify_view(request):
    job_id = request.GET.get('job_id')
    ret = {}
    ret['current_job'] = ci_utils.get_module_job(job_id)
    ret['module'] = ci_utils.get_module_list()
    ret['types'] = range(4)
    return render(request, 'ci_mgr/ci_job_opr.html', {'data': ret})


@csrf_exempt
@public.auth_user
def job_seq_view(request):
    module_id = request.GET.get('module_id')
    sub_task_id = request.GET.get('sub_task_id')
    job_id = request.GET.get('job_id')
    if module_id and sub_task_id and job_id:
        # get all jobs belong to this module
        jobs = ci_utils.get_jobs_no_seq_by_sub_task_id(sub_task_id)
        sub_task = ci_utils.get_sub_task_info(sub_task_id)
        ret = {}
        ret['module'] = ci_utils.get_module_list()
        ret['current_module'] = ci_utils.get_module_by_id(module_id)
        ret['current_job'] = ci_utils.get_job_info_by_id(job_id)
        jb_info = ci_utils.get_job_set_by_job_id_sub_task_id(job_id, sub_task_id)
        if ret['current_job']:
            if jb_info['next'] == '[]':
                ret['current_job']['next'] = []
            else:
                ret['current_job']['next'] = [int(i) for i in jb_info['next'][1:-1].split(',')]
            ret['current_job']['pre'] = jb_info['pre']
            ret['current_job']['is_start'] = jb_info['is_start']

        ret['current_subtask'] = sub_task
        ret['jobs'] = []
        for j in jobs:
            tmp = ci_utils.get_job_info_by_id(j['job_id'])
            if not tmp:
                continue
            tmp['next'] = j['next']
            tmp['pre'] = j['pre']
            tmp['is_start'] = j['is_start']
            ret['jobs'].append(tmp)

        job_tree = ci_utils.recursion_scan(ci_utils.get_sub_task_job_list(sub_task_id)['jobs'])

        # change 'next' to children
        ret['job_tree'] = []
        for i in job_tree:
            ret['job_tree'].append( '[' + json.dumps(i) + ']')
        return render(request, 'ci_mgr/ci_job_seq_config.html', {'data': ret})
    else:
        return render(request,'ci_mgr/ci_error.html')

@csrf_exempt
@public.auth_user
def job_bind_view(request):
    module_id = request.GET.get('module_id')
    sub_task_id = request.GET.get('subtask_id')
    if module_id and sub_task_id :
        # get all jobs belong to this module
        band_jobs = ci_utils.get_jobs_no_seq_by_sub_task_id(sub_task_id)
        sub_task = ci_utils.get_sub_task_info(sub_task_id)
        jobs = ci_utils.get_module_job_list(module_id)

        for j in jobs:
            for bj in band_jobs:
                if bj['job_id'] == j['id']:
                    j['binded'] = True
                    break
        ret = {}
        ret['jobs'] = jobs
        ret['current_module'] = ci_utils.get_module_by_id(module_id)
        ret['current_subtask'] = ci_utils.get_sub_task_info(sub_task_id)
        return render(request, 'ci_mgr/ci_bind_job.html',{ 'data': ret})
    else:
        return render(request, 'ci_mgr/ci_error.html')

@csrf_exempt
@public.auth_user
def dashboard_view(request):
    ret = {}
    ret['module'] = ci_utils.get_module_list()
    data = ci_utils.static_dashboard()
    last_one = []
    for l in data['latest']:
        if len(l.get('task_record')) != 0:
            last_one_tmp = l.get('task_record')[-1]
            last_one_tmp['name'] = ci_utils.get_module_by_id(last_one_tmp.get('module_id')).get('name')
            last_one.append(last_one_tmp)
        for t in l['task_record']:
            if "options" not in t:
                t["options"] = {}
            t['options']['other'] = json.dumps(t.get('options', {}).get('other'))
    ret['latest'] = ci_utils.static_dashboard().get('latest')


    """
    # test
    #last_one = [1,2,3,4,5,6,7,8,9,10,11,12]
    import random
    arr_len = random.randint(4,12)
    for x in range(arr_len):
        seed = random.randint(0,1)
        if seed:
            last_one.append({"name": 'snake' + str(seed), "status" : 3})
        else:
            last_one.append({"name": 'snake' + str(seed), "status" : 4})

    """

    if len(last_one) <= 5:
        last_one.append({"name":"待添加", "status": 10})

    line_hex = 4
    line_hex_even = 5
    # last one 蜂窝分行 4 5 4 5
    ret['last_one'] = []
    flag_even = False
    while(len(last_one) != 0):
        if not flag_even:
            flag_even = True
            if len(last_one) >= line_hex:
                ret['last_one'].append(last_one[:line_hex])
                last_one = last_one[line_hex:]
            else:
                ret['last_one'].append(last_one)
                break
        else:
            flag_even = False
            if len(last_one) >= line_hex_even:
                ret['last_one'].append(last_one[:line_hex_even])
                last_one = last_one[line_hex_even:]
            else:
                ret['last_one'].append(last_one)
                break

    # statistics

    module_list = []
    time_series = []
    ratio_series = []
    for i in range(len(data.get('latest'))):
        this_item = {}
        module_list.append(data.get('latest')[i].get("name"))
        # ci 平均时间
        this_item['name'] = data.get('latest')[i].get("name")
        this_item['type'] = 'line'
        this_item['stack'] = u'CI平均运行时间'
        if data.get('latest')[i].get('static'):
            this_item['data'] = data.get('latest')[i].get('static').get('runtime')
            if data.get('latest')[i].get('static').get('runtime') == None:
                this_item['data'] = [0,0,0,0,0]

            elif len(data.get('latest')[i].get('static').get('runtime')) < 5:
                this_item['data'].append([0] * (5-len(data.get('latest')[i].get('static').get('runtime'))))
        else:
            this_item['data'] = [0,0,0,0,0]
        time_series.append(this_item)

        # ci 成功率
        this_ratio = {}
        this_ratio['name'] = data.get('latest')[i].get('name')
        this_ratio['center'] =  json.dumps( [ str((i%5)*20 + 10) + "%" ,str((i/5 + 1)*30) + "%"] )
        this_ratio['x'] = str((i%5 )*20) + "%"
        tmp_data = []
        if data.get('latest')[i].get('static'):
            tmp_data.append({'name': 'other', 'value': 100- int(str(int(data.get('latest')[i]['static']['success_rate']*100))[:2])})
            tmp_data.append({'name': data.get('latest')[i].get('name'), 'value': int(str(int(data.get('latest')[i]['static']['success_rate']*100))[:2])})
            this_ratio['data'] = tmp_data
            ratio_series.append(this_ratio)

        #this_ratio['data']

    ret['ratios'] = ratio_series
    ret['runtime_series'] = json.dumps(time_series)



    return render(request, 'ci_mgr/ci_dashboard.html', {'data': ret})



# job monitor
@csrf_exempt
@public.auth_user
def job_job_show_view(request):
    ret = {}
    all_job = job_utils.get_job_all()
    all_trees = all_job.get('jobs')
    # calculate tree width
    ret['trees'] = []
    ret['exclude'] = all_job.get('exclude')

    for i in job_utils.recursion_scan(all_trees):
        i['chart_data'] = '[' + json.dumps(i) + ']'
        job_utils.calculate_width([i],len([i]))
        i['width'] = max(job_utils.width_list)
        i['width_px'] = 80 + 80 + (i['width']-1) * (20 + 8) # 上下间距：50 每个树枝之间20px
        ret['trees'].append(i)


    return render(request,'job_mgr/job_show.html',{'data': ret})


@csrf_exempt
@public.auth_user
def job_job_config_view(request):
    type = request.GET.get('type')
    ret= {}
    ret['jobs'] = []
    jobs = job_utils.get_job_list()
    if type == 'tag':
        for i in jobs:
            if i['flag'] == 0:
                ret['jobs'].append(i)
    elif type == 'notag':
        for i in jobs:
            if i['flag'] == 1:
                ret['jobs'].append(i)
    else:
        ret['jobs'] = jobs

    all_job = job_utils.get_job_all()
    all_trees = all_job.get('jobs')
    ret['trees'] = []
    ret['exclude'] = all_job.get('exclude')

    for i in job_utils.recursion_scan(all_trees):
        i['chart_data'] = '[' + json.dumps(i) + ']'
        job_utils.calculate_width([i],len([i]))
        i['width'] = max(job_utils.width_list)
        i['width_px'] = 80 + 80 + (i['width']-1) * (20 + 8) # 上下间距：50 每个树枝之间20px
        ret['trees'].append(i)

    return render(request,'job_mgr/job_config.html',{'data':ret})

@csrf_exempt
@public.auth_user
def job_seq_config_view(request):
    job_id = request.GET.get('id')
    ret= {}
    ret['jobs'] = job_utils.get_job_list()
    ret['current_job'] = job_utils.get_job(job_id)
    return render(request,'job_mgr/job_seq_config.html',{'data':ret})

@csrf_exempt
@public.auth_user
def job_hex_view(request):
    ret = []
    jobs = job_utils.static_job()
    line = []
    even_line = []
    even_flag = False
    for i in jobs:
        if even_flag == False: # 4 items per line
            if len(line) < 3 :
                line.append(i)
            else:
                even_line.append(i)
                ret.append(line)
                line = []
                even_flag = not even_flag
        else: # 5 items per line
            if len(even_line) < 4 :
                even_line.append(i)
            else:
                line.append(i)
                ret.append(even_line)
                even_line = []
                even_flag = not even_flag

    if len(line):
        ret.append(line)

    if len(even_line):
        ret.append(even_line)

    return render(request, 'job_mgr/job_hex.html',{'data':ret})



# assess

@csrf_exempt
@public.auth_user
def train_algorithm(request):
    scene_id = request.GET.get('scene_id')
    if scene_id:
        # get scene info  TODO

        ret = {}
        return render(request, 'assess/train_algorithm.html', {'data': ret})
    else:
        return render(request, 'error.html')

@public.auth_user
def get_user_view(request):
    data = {}
    work_id = int(request.GET.get("work_id")) if request.GET.get("work_id") else 0
    data["work_id"] = work_id
    data["q"] = request.GET.get("q", "")
    data["flag"] = request.GET.get("flag", "")
    data["page_current"] = request.GET.get("page_current", 1)
    ret = data
    ret["user"] = utils.get_user_info(data)
    ret["auth"] = utils.check_auth(public.get_user_mail(request), work_id)
    return render(request, 'user_info.html', {'data': ret})

@csrf_exempt
@public.auth_user
def set_auth_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        ret = utils.set_auth(request)
        if ret:
            return public.fail_result_http(ret)
        return public.success_result_http(ret)



def pre_launch(request):
    return render(request, "pre_new.html")


def sheet(request):
    return render(request, "sheet.html")

def get_pre_launch_info(request):
    public_date = data_utils.get_public(request)
    group_id = public_date.get('group_id')
    # 默认 newlab
    name = "agile"
    ret = {}
    """
    ret['version'] = data_utils.get_seal_or_newlab_version()
    """

    ret['online'] = []

    ret['data'] = {}
    ret['data']['jobs'] = []

    content = data_utils.get_online_package()


    if int(group_id) == 0:  # others
        group_job = data_utils.get_jobs_not_group()
    else:
        group_job = data_utils.get_group_jobs(group_id)

    for i in group_job:
        if i['name'].startswith("newlabs_"):
            tmp_job_name = i['name']
            i['jobname'] = tmp_job_name
            i['name'] = i['name'][8:]

            # get specific info
            job = data_utils.JenkinsInfo(name=name, job = tmp_job_name)
            if job.get_status() == False:
                continue
            this_ret = job.get_ret()

            if not this_ret.get('lastBuild'):
                this_ret['lastBuild'] = {}

            i['url'] = this_ret.get('url')
            # get seald version info and operator
            this_oper_info = data_utils.get_latest_job_record(i['jobname'])
            i['sealed_version'] = this_oper_info['sealed_version']
            online_info = data_utils.get_latest_online_version(content, i['jobname'])


            if online_info != False:
                i['has_online_version'] = True
                i['online_version'] = online_info

                tmp_dict = {}
                tmp_dict['jobname'] = i['jobname']
                tmp_dict['online_version'] = online_info
                ret['online'].append(tmp_dict)
            else:
                i['has_online_version'] = False

            i['newlab_version'] = this_oper_info['newlab_version']
            i['user'] = this_oper_info['user']

            if this_ret['color'] == 'blue':
                i['lastbuild_status'] = 'success'
            elif this_ret['color'] == 'disabled':
                i['lastbuild_status'] ='disabled'
            elif this_ret['color'] == 'notbuilt':
                i['lastbuild_status'] ='notbuilt'
            elif this_ret['color'].find('anime'):
                i['lastbuild_status'] ='building'
            else:
                i['lastbuild_status'] = 'fail'


            if 'number' in this_ret['lastBuild']:
                i['lastBuild'] = this_ret['lastBuild']['number']
            else:
                i['lastBuild'] = ""

            if 'url' in this_ret['lastBuild']:
                i['lastBuild_console'] = this_ret['lastBuild']['url'] + 'console'
                i['lastBuild_consoleText'] = this_ret['lastBuild']['url'] + 'consoleText'
            else:
                i['lastBuild_console'] = ''
                i['lastBuild_consoleText'] = ''

            i['view'] = name
            i['buildable'] = this_ret['buildable']
            i['trigger_url'] = "http://jenkins.meiliworks.com/view/" + name + "/job/" + tmp_job_name + "/build?delay=0sec"

            if len(this_ret['property']) != 1:
                # 需要参数  目前支持1个参数

                this_param_info = this_ret['property'][1]['parameterDefinitions'][0]
                i['trigger_param'] = this_param_info['name']
                i['trigger_param_description'] = this_param_info['description']
                tmp_default_param = {}
                tmp_default_param[this_param_info["defaultParameterValue"]['name'].encode("utf-8")] = this_param_info["defaultParameterValue"]['value'].encode("utf-8")
                i['trigger_default_param'] = json.dumps(tmp_default_param)

            else:
                # 不需要参数, 都设成 ‘none’ 供前端判断
                i['trigger_param' ] = 'none'
                i['trigger_default_param'] = 'none'

            # add classification
            ret['data']['jobs'].append(i)


    #获取用户权限信息
    ret["data"]["public"] = public_date

    return public.success_result_http(ret['data'])


def get_seal_version(request):
    module = request.GET.get('module')
    if module == 'biz':
        return public.success_result_http(data_utils.get_seal_or_newlab_version('biz'))
    elif module == "shanghaife":
        return public.success_result_http(data_utils.get_seal_or_newlab_version('shanghaife'))
    else:
        return public.success_result_http({'biz': data_utils.get_seal_or_newlab_version('biz'), "shanghaife": data_utils.get_seal_or_newlab_version('biz')})

@public.auth_user
def sheet_version(request):
    public_date = data_utils.get_public(request)
    group_id = request.GET.get('group_id')
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1

    ret = {}
    ret['group_id'] = group_id
    ret['data'] = {}
    ret['data']['public'] = public_date
    try:
        all_info = requests.get(public.JAVA_HOST + '/onlinecard/api/group_versions?group=' + str(group_id) + "&page=" + str(page)).json()
        group_version = all_info.get('data')
    except:
        all_info = {}
        group_version = []


    if all_info.get('pageCount'):
        ret['last_page'] = int(all_info.get('pageCount'))
    else:
        ret['last_page'] = 0


    if ret['last_page'] <= 5:
        ret['pages'] = range(1, ret['last_page'] + 1)
    else:
        if page < 3:
            ret['pages'] = range(1,6)
        else:
            if page + 3 <= ret['last_page']:
                ret['pages'] = range(page-2,page+3)
            elif page < ret['last_page']:
                if ret['last_page'] - 5 < page:
                    ret['pages'] = range(ret['last_page']-4, ret['last_page']+1)
                else:
                    ret['pages'] = range(page-2,ret['last_page']+1)
            else:
                ret['pages'] = range(page-4, page+1)

    ret['page'] = page
    ret['group_id'] = group_id
    ret['pre'] = page - 1
    if page == ret['last_page']:
        ret['next'] = -1
    else:
        ret['next'] = page + 1

    if len(group_version) <10:
        ret['next'] = -1

    if len(group_version) != 0:
        ret['version_info'] = group_version
        return render(request, "sheet_version.html", ret)
    else:
        return render(request, "sheet_version.html", [])
    return render(request, "sheet_version.html", ret)


def sheet_small_module_log(request):
    module_id = request.GET.get('module_id')
    seal_version = request.GET.get('seal_version')
    online_version = request.GET.get('online_version')
    log_info = requests.get(public.JAVA_HOST + "/onlinecard/api/svn_logs?module_id=" + module_id + "&seal_version=" + seal_version + "&online_version=" + online_version).json()
    return render(request, "sheet_small_module_log.html", {'data': log_info})


def sheet_preview(request):
    group_version_id = request.GET.get('group_version_id')
    group_id = request.GET.get('group_id')
    try:
        pre_view_info = requests.get(public.JAVA_HOST + '/onlinecard/api/onlinecard/preview?group_version_id=' + group_version_id).json()
    except:
        pre_view_info = {}

    print pre_view_info
    if pre_view_info.get('product_cards'):
        for i in pre_view_info.get('product_cards'):
            if i.get('need_qa'):
                if not pre_view_info.has_key('need_qa'):
                    pre_view_info['need_qa'] = []
                pre_view_info['need_qa'].append(i)
            else:
                if not pre_view_info.has_key('not_need_qa'):
                    pre_view_info['not_need_qa'] = []
                pre_view_info['not_need_qa'].append(i)

    pre_view_info['group_id'] = group_id
    pre_view_info['group_version_id'] = group_version_id

    return render(request, "sheet_preview.html", {'data': pre_view_info})

