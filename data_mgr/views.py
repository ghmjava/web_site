# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import collections

import public
import utils
import datetime

from exception_mgr.utils import catch_exception_http

from web_mgr import utils as web_utils

logger = logging.getLogger("web_site.data_mgr.util")


@csrf_exempt
@catch_exception_http
def save_dashboard_view(request):
    logger.debug(request)
    if request.method == "POST":
        data = json.loads(request.body)
        err = utils.save_dashboard(data)
        if err:
            return public.fail_result_http(err, data)
    else:
        return public.fail_result_http(u"该接口只支持POST数据")
    return public.success_result_http()


@csrf_exempt
@catch_exception_http
def save_promotion_record_view(request):
    logger.debug(request)
    if request.method == "POST":
        data = json.loads(request.body)
        err = utils.save_promotion_record(data)
        if err:
            return public.fail_result_http(err, data)
    else:
        return public.fail_result_http(u"该接口只支持POST数据")
    return public.success_result_http()



@catch_exception_http
def get_dashboard_view(request):
    if request.method == "GET":
        data = request.GET
        ret = utils.get_dashboard(data)
        return public.success_result_http(ret)

@catch_exception_http
def get_dashboard_info_view(request):
    request.GET = request.GET.copy()
    data = request.GET
    ret = utils.get_dashboard_info(data, num=None)
    return public.success_result_http(ret)

@catch_exception_http
def static_dashboard_view(request):
    env = request.GET.get("env")
    if env.upper() == public.ENV_MOB:
        ret = utils.static_mob()
    else:
        ret = utils.static_newlab()
    return public.success_result_http(ret)

@catch_exception_http
def get_interface_info_view(request):
    if request.method == "GET":
        ret = utils.get_interface_info()
        return public.success_result_http(ret)

@catch_exception_http
def get_promotion_record_view(request):
    if request.method == "GET":
        ret = utils.get_promotion_record()
        return public.success_result_http(ret)

@csrf_exempt
@catch_exception_http
def save_svn_history_view(request):
    logger.debug(request)

    if request.method == "POST":
        data = json.loads(request.body)
        utils.save_svn_history(data)
    else:
        return public.fail_result_http(u"该接口只支持POST数据")
    return public.success_result_http()

@catch_exception_http
def get_svn_history_view(request):
    data = {}
    data["create"] = request.GET.get("create")
    data["module"] = request.GET.get("module")
    ret = utils.get_svn_history(data)
    return public.success_result_http(ret)

@csrf_exempt
@catch_exception_http
def save_auto_report(request):
    """
    存储推送来的数据！-autoreport
    jichaoliu
    """
    if request.method == "POST":
        data = json.loads(request.body)
        err = utils.save_get_report(data)
        if err:
            return public.fail_result_http(err, data)
    else:
        return public.fail_result_http(u"该接口只支持POST数据")
    return public.success_result_http()

@catch_exception_http
def get_sealed_info(request):
    """
    :author: yechengzhou
    :param request:
    :return: sealed release diff info json
    """
    if request.method == "GET":
        data = request.GET
        ret = utils.get_sealed_info()
        return public.success_result_http(ret)


@csrf_exempt
@catch_exception_http
def save_sealed_info(request):
    """
    :author: yechengzhou
    :param request: json
    :return: err msg, None means success
    """
    if request.method == "POST":
        data = json.loads(request.POST.get('retjson'))
        err = utils.save_sealed_info(data)
        if err:
            return public.fail_result_http(err, data)
        else:
            return public.success_result_http()

    else:
        return public.fail_result_http(u"该接口只支持POST数据")

@catch_exception_http
def get_sealed_info(request):
    """
    :author: yechengzhou
    :param request: day
    :return: json
    """
    if request.method == "GET":
        try:
            day = request.GET.get("day")
            ret = utils.get_sealed_info(day)
        except:
            ret = utils.get_sealed_info()

        if ret:
            return public.success_result_http(ret)
        else:
            return public.fail_result_http(u"封板信息为空")


@catch_exception_http
def get_sealdiffonline(request):
    """
    :author: yechengzhou
    :param request: day
    :return: json
    """
    if request.method == "GET":
        try:
            day = request.GET.get("day")
            ret = utils.get_sealdiffonline(day)
        except:
            ret = utils.get_sealdiffonline()


        if ret == 1:
            return public.fail_result_http(u"上线信息空")
        elif ret:
            return public.success_result_http(ret)
        else:
            return public.fail_result_http(u"diff信息不存在")


@catch_exception_http
def get_branch_svn_log(request):
    """
    :author: yechengzhou
    :param request: request should contains branch name and module name
    :return: json format branch svn log
    """
    if request.method != "GET":
        return public.fail_result_http(u"该接口只支持GET")
    else:

        module = request.GET.get('module')
        branch = request.GET.get('branch')
        type = request.GET.get('type') # 0 -- one day  1 -- last 10

        if not (module and branch):
            return public.fail_result_http(u"参数错误")

        else:
            if type == '0' or type == None:
                if branch != "trunk":
                    start = branch.split('_')[-2]
                    start_time = public.str2datetime(start, "%Y%m%d")
                    end_time = start_time + datetime.timedelta(days=1)
                    end = public.datetime2str(end_time, "%Y%m%d")
                    ret = utils.get_branch_svn_log(module,branch, start, end)
                else:
                    ret = utils.get_branch_svn_log(module,branch)


            elif type == '1':
                ret = utils.get_branch_svn_log(module,branch )


            return public.success_result_http(ret)

@catch_exception_http
def get_module_svn_history(request):
    if request.method != "GET":
        return public.fail_result_http("Only support GET")

    module = request.REQUEST['module']
    if module and module != 'undefined':
        job_name = "newlabs_" + module
    else:
        return public.fail_result_http('module name is not provided or not usable')
    # get last 5 job record
    job_record_list = utils.get_job_record_by_type_job_name(job_name,3,5)
    job_record_list.reverse()
    # get last 10 svn class
    svn_list = utils.get_branch_svn_log(module,"trunk")
    svn_list.reverse()

    # merge 2 list sort by time
    """
        data['comment'] = u"封板"
        data['version'] = i.version
        data['user'] = i.mail
        data['time'] = i.ctime
    """
    ret = []
    while len(job_record_list) != 0 and len(svn_list) != 0:
        if job_record_list[0]['time'] > svn_list[0]['time'][:19]:
            svn_list[0]["time"] = svn_list[0]['time'][:19]
            ret.append(svn_list[0])
            del svn_list[0]
        else:
            ret.append(job_record_list[0])
            del job_record_list[0]
    ret.extend(job_record_list )
    ret.extend(svn_list)

    return public.success_result_http({'data': ret})


@csrf_exempt
@catch_exception_http
def jenkins_trigger(request):
    """
    :author: yechengzhou
    :param request: contains trigger para
    :return:
    """
    if request.method != "POST":
        return public.fail_result_http(u"该接口只支持POST")
    else:
        """
        data is a json
        {
            "name" : "branch_name",
            "value" : "lab1:172.16.7.201"
        }
        """
        """
        # 添加用户操作记录
        this_option = models.JenkinsUser()
        this_option.type = 2
        tmp_arr = request.REQUEST['url'].split("/")
        this_option.jobname = tmp_arr[tmp_arr.index('job') + 1]
        this_option.viewname = "newlab"
        this_option.optiontime = public.str2datetime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "%Y-%m-%d %H:%M:%S")
        # get user info
        user_info = web_utils.get_user_cookie(request)
        this_option.mail = user_info['mail']
"""
        user_dict = {}
        user_dict['usermail'] = public.get_user_mail(request)


        this_request_dict = dict(request.REQUEST)

        if "url" in request.REQUEST:
            if request.REQUEST.get('daily') == "merge":
                # 对 biz shanghaife 做特殊处理
                if 'biz' in request.REQUEST['url'] or 'shanghaife' in request.REQUEST['url']:
                    module_name = request.REQUEST['branch_num']
                    # get latest sealed version
                    #get jobname from url
                    this_url = request.REQUEST['url']
                    job_name = this_url[this_url.find("/job/") + 5 : this_url.find("/build?")]
                    job_name = job_name + "_" + request.REQUEST['branch_num']
                    this_record = utils.get_latest_job_record(job_name,True)



                    if this_record['sealed_version'] == 'unknown':
                        return public.fail_result_http(u'此模块没有封板信息，不能合入')

                    this_request_dict['branch_num'] = this_record['sealed_version']

                else:
                    this_url = request.REQUEST['url']
                    job_name = this_url[this_url.find("/job/") + 5 : this_url.find("/build?")]
                    this_record = utils.get_latest_job_record(job_name)
                    if this_record['sealed_version'] == 'unknown':
                            return public.fail_result_http(u'此模块没有封板信息，不能合入')

            JT = utils.JenkinsTrigger(this_request_dict['url'],this_request_dict,user_dict)
            if JT.trigger():
                return public.success_result_http()
            else:
                return public.fail_result_http(u"jenkins触发有错误")
        else:
            return public.fail_result_http(u"缺少触发url")

@csrf_exempt
@catch_exception_http
def jenkins_info(request):
    """
    :author: yechengzhou
    :param request:
    :return:
    """
    if request.method != "GET":
        return  public.fail_result_http(u'该接口只支持GET')
    if 'name' in request.REQUEST:
        if 'job' in request.REQUEST:
            logging.debug('')
            job = utils.JenkinsInfo(name=request.REQUEST['name'], job=request.REQUEST['job'])
            if job.get_status():
                return public.success_result_http(json.dumps(job.get_ret()))
            else:
                return public.fail_result_http(u'get jenkins info failed')
        else:
            view = utils.JenkinsInfo(name=request.REQUEST['name'])
            if view.get_status():
                return public.success_result_http(json.dumps(view.get_ret()))
            else:
                return public.fail_result_http(u'get jenkins info failed')

    else:
        return public.fail_result_http(u"wrong argument")


@csrf_exempt
@catch_exception_http
def jenkins_builds_info(request):
    """
    :author: yechengzhou
    :param request:
    :return:
    """
    if request.method != "GET":
        return  public.fail_result_http(u'该接口只支持GET')
    if 'name' in request.REQUEST and 'job' in request.REQUEST:

        job = utils.JenkinsInfo(name=request.REQUEST['name'], job=request.REQUEST['job'])
        if job.get_status():
            builds = job.get_ret()['builds']
            builds_url = []
            for i in builds:
                builds_url.append(i['url'])
            ret =  utils.get_build_specific_info(builds_url)
            return public.success_result_http(ret)
        else:
            return public.fail_result_http(u'get jenkins info failed')
    else:
        return public.fail_result_http(u"wrong argument")


@csrf_exempt
@catch_exception_http
def jenkins_switch(request):
    """
    :author: yechengzhou
    :param request: contains trigger para
    :return:
    """
    if request.method != "POST":
        return public.fail_result_http(u"该接口只支持POST")
    else:
        """
        data is a json
        {
            "on_off" : "branch_name",
            "url" : job url
        }
        """
        """
        # 添加用户操作记录
        this_option = models.JenkinsUser()
        if request.REQUEST['on_off'] == "enable":
            this_option.type = 1
        elif request.REQUEST['on_off'] == "disable":
            this_option.type = 0
        tmp_arr = request.REQUEST['url'].split("/")
        this_option.jobname = tmp_arr[tmp_arr.index('job') + 1]
        this_option.viewname = "newlab"
        this_option.optiontime = public.str2datetime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "%Y-%m-%d %H:%M:%S")
        # get user info
        user_info = web_utils.get_user_cookie(request)
        this_option.mail = user_info['mail']
        """
        if request.REQUEST['on_off'] == "enable":
            type = 1
        elif request.REQUEST['on_off'] == "disable":
            type = 0
        if "url" in request.REQUEST and "on_off" in request.REQUEST:
            JT = utils.JenkinsJobSwitch(request.REQUEST['url'],request.REQUEST['on_off'])
            if JT.switch():
                #this_option.save()
                this_info = {}
                this_info['view_name'] = 'agile'
                this_url = request.REQUEST.get('url')
                this_info['job_name'] = this_url[this_url.find("/job/") + 5 : this_url.find("/build?")]
                this_info['type'] = type
                this_info['version'] = ""

                utils.save_job_record(request, this_info)
                return public.success_result_http()
            else:
                return public.fail_result_http(u"jenkins触发有错误")
        else:
            return public.fail_result_http(u"缺少触发参数，需要url和on_off")


@catch_exception_http
def save_job_record_view(request):
    utils.save_job_record(request)
    return public.success_result_http()



@catch_exception_http
def get_build_status(request):
    if request.method != "GET":
        return public.fail_result_http(u"do not accept get method")
    else:
        job_name = request.REQUEST.get('name')
        view = request.REQUEST.get('view')


        # build = request.REQUEST.get('build')

        # 目前只有newlab
        if job_name and job_name != 'undefined' and not job_name.startswith("newlabs"):
            job_name = "newlabs_" + job_name
        else:
            return public.fail_result_http('get job name failed')

        view = "agile"
        JB = utils.JenkinsInfo(view, job_name)
        build = JB.get_ret()['builds'][0]['number']

        JI = utils.JenkinsInfo(view, job_name, str(build))
        if JI.get_status():
            if_building = JI.get_ret()['building']
            if JI.get_ret()['result']:
                job_status = JI.get_ret()['result'].lower()
            else:
                job_status = 'fail'
            return public.success_result_http({"status":job_status, 'building': if_building})
        else:
            logging.error("Get Job Info Failed:" + str(request))
            return public.fail_result_http('get job info failed')


@catch_exception_http
def get_sealed_or_newlab_version(request):
    # 获取封板号 封板号没有就返回newlab版本
    if request.method != "GET":
        return public.fail_result_http(u"Only support GET")
    else:
        ret = utils.get_seal_or_newlab_version(request.REQUEST.get("module"))
        return public.success_result_http(ret)

@catch_exception_http
def get_branch_diff(request):
    if request.method != "GET":
        return public.fail_result_http(u"Only support GET")
    else:
        if request.REQUEST.get('module') and request.REQUEST.get('b1') and request.REQUEST.get('b2'):
            ret = utils.diff_branch(request.REQUEST.get('module') , request.REQUEST.get('b1'), request.REQUEST.get('b2'))
            if ret == False:
                return public.fail_result_http("branch error","branch可能有问题，请检查svn下是否有对应branch")
            else:
                if ret == "":
                    ret = u"两个branch的代码无差别"
                return public.success_result_http(ret)
        else:
            return public.fail_result_http(u"miss some argument, module & b1 &b2 needed")



@catch_exception_http
def get_history_by_module(request):
    if request.method != "GET":
        return public.fail_result_http(u"Only support GET")
    else:
        para = {}
        para["module"] = request.REQUEST.get('module')
        version = request.REQUEST.get('version') # branch num
        # RB_vdoota_20150720_103028
        tmp_list = version.split("_")

        para["end"] = tmp_list[-2] + tmp_list[-1]

        return public.success_result_http(utils.get_svn_history_test(para))


@catch_exception_http
def get_latest_online_version(request):
    if request.method != "GET":
        return public.fail_result_http(u'Only support GET')
    else:
        if request.REQUEST.get("jobname"):
            print "bingo",request.REQUEST.get("jobname")
            ret = utils.get_latest_online_version(request.REQUEST.get("jobname"))
            return public.success_result_http(ret)
        else:
            return public.fail_result_http(u'please provide jobname')

def get_online_package_view(request):
    ret = utils.get_online_package()
    return public.success_result_http(ret)

def trigger_online_package_view(request):
    ret = utils.trigger_online_package()
    return public.success_result_http(ret)

@public.auth_user
def get_group_view(request):
    id = request.GET.get("id")
    ret = utils.get_group(id)
    return  public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_group_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        body = request.POST
        data = {}
        if body.get("id"):
            data["id"] = body.get("id")
        data["name"] = body.get("name")
        data["desc"] = body.get("desc")
        id = utils.save_group(data)
        return redirect("/jenkins?group_id=%s" % id)

@public.auth_user
@csrf_exempt
def rm_group_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        body = json.loads(request.body)
        ret = utils.rm_group(body.get("id"))
        if ret != True:
            return public.fail_result_http(ret)
        return public.success_result_http(ret)

@public.auth_user
def get_job_info_view(request):
    id = request.GET.get("id")
    ret = utils.get_job_info(id)
    return  public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def bind_job_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        data = json.loads(request.body)
        ret = utils.bind_job(data)
        return public.success_result_http(ret)

@public.auth_user
def get_collection_view(request):
    ret = utils.get_collection(request)
    return  public.success_result_http(ret)

@public.auth_user
@csrf_exempt
def save_collection_view(request):
    if request.method != "POST":
        return public.fail_result_http(u"Only support POST!")
    else:
        ret = utils.save_collection(request)
        return public.success_result_http(ret)

@public.auth_user
def get_job_html_view(request):
    group_id = request.GET.get("group_id")
    ret = utils.get_job_html(group_id)
    return HttpResponse(ret)

##################################以下为页面###########################################
@public.auth_user
def group_view(request):
    data = {}
    data["public"] = utils.get_public(request)
    data["group"] = utils.get_group()
    return render(request, 'data_mgr/group.html', {"data":data})

@csrf_exempt
@public.auth_user
def pre_launch_view(request):
    public_date = utils.get_public(request)
    group_id = public_date.get("group_id")

    ret = {}
    ret['version'] = utils.get_seal_or_newlab_version()
    ret['biz_version'] = utils.get_seal_or_newlab_version('biz')
    ret['shanghaife_version'] = utils.get_seal_or_newlab_version('shanghaife')

    ret['online'] = []

    ret['data'] = {}
    ret["data"]["public"] = public_date
    ret['data']['jobs'] = utils.get_group_jobs(group_id)
    return render(request,"data_mgr/prelaunch.html", ret)

