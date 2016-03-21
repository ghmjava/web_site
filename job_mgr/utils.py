# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''
import json
import copy
import time
from django.forms.models import model_to_dict
import jenkins

import models
import public


def save_job(data):
    name = data.get("name")
    if not name:
        return u"名称不能为空"
    url = data.get("url")
    flag = 0
    if url:
        flag = 1
    user = data.get("user")
    pre_id = int(data.get("pre_id")) if data.get("pre_id") else -1
    job_id = data.get("id")
    if job_id:
        job_info = models.JobInfo.objects.get(id=job_id)
    else:
        job_info = models.JobInfo()
        job_info.pre_id = pre_id
    job_info.name = name
    job_info.url = url
    job_info.user = user
    job_info.flag = flag
    job_info.save()

def get_job(id):
    job_info = models.JobInfo.objects.get(id=id)
    ret = model_to_dict(job_info)
    ret["options"] = json.loads(ret.get("options", "{}"))
    job_info = models.JobInfo.objects.filter(pre_id=ret["id"])
    ret["next"] = []
    for job in job_info:
        ret["next"].append(model_to_dict(job))
    return ret

def get_job_list():
    job_infos = models.JobInfo.objects.all()
    ret = []
    for job in job_infos:
        tmp = model_to_dict(job)
        ret.append(tmp)
    return ret

def get_job_all():
    job_infos = models.JobInfo.objects.all()
    job_info = job_infos.filter(pre_id=0)
    ret = {}
    ret["jobs"] = []
    ret["deep"] = 0
    for job in job_info:
        tmp = model_to_dict(job)
        ret["jobs"].append(recursion(tmp))
    job_info = job_infos.filter(pre_id=-1)
    ret["exclude"] = []
    for job in job_info:
        ret["exclude"].append(model_to_dict(job, exclude=["options"]))
    return ret

def set_next_job(data):
    id = data.get("id")
    if not id:
        return u"缺少参数id"
    next_list = data.get("next_list") if data.get("next_list") else 0
    if not isinstance(next_list, list):
        next_list = [next_list]
    pre_id_list = get_pre_list(id)
    for n in next_list:
        if n in pre_id_list:
            return u"后置job中包含前置job，设置失败！"
    models.JobInfo.objects.filter(pre_id=id).update(pre_id=-1)
    models.JobInfo.objects.filter(id__in=next_list).update(pre_id=id)
    is_start = data.get("is_start")
    if is_start:
        models.JobInfo.objects.filter(id=id).update(pre_id=0)

def get_pre_list(id):
    job_info = models.JobInfo.objects.all()
    current = job_info.get(id=id)
    pre_id = current.pre_id
    pre_list = []
    while pre_id != 0 and pre_id != -1:
        pre_list.append(pre_id)
        current = job_info.get(id=pre_id)
        pre_id = current.pre_id
    return pre_list

def rm_job(id):
    job = models.JobInfo.objects.get(id=id)
    pre_id = job.pre_id
    next_job = models.JobInfo.objects.filter(pre_id=id)
    if pre_id:
        next_job.update(pre_id=pre_id)
    else:
        next_job.update(pre_id=0)
    job.delete()

status = {}
status["pass"] = 0
status["fail"] = 0
status["other"] = 0
status["total"] = 0

def static_job():
    jobs = models.JobInfo.objects.filter(flag=0)
    ret = []
    for job in jobs:
        status["pass"] = 0
        status["fail"] = 0
        status["other"] = 0
        status["total"] = 0
        tmp = model_to_dict(job)
        rec = recursion(tmp)
        rec["static"] = copy.deepcopy(status)
        del rec["next"]
        ret.append(rec)
    return ret

def recursion(data):
    id = data.get("id")
    data["next"] = []
    jobs = models.JobInfo.objects.filter(pre_id=id)
    for job in jobs:
        tmp = model_to_dict(job)
        tmp["options"] = json.loads(tmp["options"])
        if tmp["flag"] != 0:
            status["total"] += 1
            if tmp['status'] == public.JENKINS_PASS:
                status["pass"] += 1
            elif tmp['status'] == public.JENKINS_FAIL:
                status["fail"] += 1
                tmp["fail_timestamp"] = int(time.time() - time.mktime(job.update_time.timetuple()))
            else:
                status["other"] += 1
        data["next"].append(recursion(tmp))
    return data


def recursion_scan(tree):

    for i in tree:
        i['children'] = i['next']
        if i.get('fail_timestamp'):
            i['name'] += u'\n(已失败' + str(time.strftime('%H:%M:%S', time.gmtime(int(i.get('fail_timestamp'))))) + ")"
        if i['flag'] == 0:
            i["itemStyle"] = {"normal": {"color": '#FF8000'}}
        else:
            if i['status'] == public.JENKINS_PASS:
                i["itemStyle"] = {"normal": {"color": '#5cb85c'}}
            elif i['status'] == public.JENKINS_FAIL:
                i["itemStyle"] = {"normal": {"color": '#d9534f'}}
            elif i['status'] == public.JENKINS_RUN:
                i["itemStyle"] = {"normal": {"color": '#5bc0de'}}
            else:
                i["itemStyle"] = {"normal": {"color": '#D8D8D8'}}

        if i.get('next') != None:
            recursion_scan(i['next'])
        else:
            continue
    return tree


width_list = []
def calculate_width(tree, max_width):
    for i in tree:
        if i.get('next') != None:
            max_width -= 1
            max_width += len(i['next'])
            width_list.append(max_width)
            calculate_width(i['next'], max_width)
        else:
            continue
    return max_width


def auto_check_job_status():
    job_info = models.JobInfo.objects.filter(flag=1)
    for job in job_info:
        try:
            url = job.url
            if not url:
                continue
            j = jenkins.Jenkins(url, public.JENKINS_USER, public.JENKINS_PASSWORD)
            ret = j.get_info()
            color = ret.get("color").encode("UTF-8")
            if public.JENKINS_COLOR_DISABLED == color:
                status = public.JENKINS_DISABLED
            elif public.JENKINS_COLOR_NOT_BUILD == color:
                status = public.JENKINS_NOT_BUILD
            elif public.JENKINS_COLOR_PASS == color:
                status = public.JENKINS_PASS
            elif public.JENKINS_COLOR_FAIL == color:
                status = public.JENKINS_FAIL
            elif public.JENKINS_COLOR_RUN in color:
                status = public.JENKINS_RUN
            else:
                status = 0

            if status != job.status:
                job.status = status
                job.options = json.dumps(ret.get("lastUnsuccessfulBuild") if ret.get("lastUnsuccessfulBuild") else {})
                job.save()
        except:
            pass




