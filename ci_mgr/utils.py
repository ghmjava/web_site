# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''
import public
import models
import socket
import json
import time
import cgi
from datetime import datetime
from django.forms.models import model_to_dict

import jenkins
import values


class MyException(Exception):
    '''General exception type for jenkins-API-related failures.'''
    pass


class Jenkins(jenkins.Jenkins):
    def __init__(self, url=public.JENKINS_URL + "/view/CI",
                 username="auto_test", password="auto_test", timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.jenkins_url = public.JENKINS_URL
        self.ci_url = url
        self.user = username
        self.password = password
        self.ci_jenkins = jenkins.Jenkins(self.ci_url, self.user, self.password)

        if url[-1] == '/':
            self.server = url
        else:
            self.server = url + '/'
        if username is not None and password is not None:
            self.auth = jenkins.auth_headers(username, password)
        else:
            self.auth = None
        self.crumb = None
        self.timeout = timeout

    def _get_view_url(self, view_name):

        view_url = "%s/view/%s" % (self.ci_url, view_name)
        return view_url

    def get_all(self):
        views = self.get_views()
        ret = []
        for view in views:
            tmp = {}
            tmp["view_name"] = view.get("name")
            tmp["view_url"] = view.get("url")
            tmp["jobs"] = self.get_view_jobs(tmp["view_name"])
            ret.append(tmp)
        return ret

    def get_view_jobs(self, view_name):
        ret = []
        j = jenkins.Jenkins(self._get_view_url(view_name), self.user, self.password)
        data = j.get_jobs()
        for d in data:
            color = d.get("color")
            if color == "disabled":
                d["status"] = public.JENKINS_DISABLED
            elif color == "notbuilt":
                d["status"] = public.JENKINS_NOT_BUILD
            elif color == "blue":
                d["status"] = public.JENKINS_PASS
            elif color == "red":
                d["status"] = public.JENKINS_FAIL
            else:
                d["status"] = public.JENKINS_UNKNOWN
            ret.append(d)
        return ret

    def create_view(self, view_name):
        ret = {"status": "success", "error": ""}
        try:
            conf_xml = values.VIEW_CONFIG_XML % (view_name)
            self.ci_jenkins.create_view(view_name, conf_xml)
        except Exception, e:
            ret["status"] = "fail"
            ret["error"] = e.message
        return ret

    def create_view_job(self, data, conf="JOB_CONFIG_XML", request=None):
        '''
        {
            "view_name":"test",
            "job_name":"hello",
            "job_detail":{
                "description":"just a test",
                "command":"ls -l",
                "params":[
                    {
                        "name":"branch_num",
                        "description":"just a test",
                        "default_value":"trunk"
                    },
                    {
                        "name":"version",
                        "description":"121212",
                        "default_value":""
                    }
                ]
            }
        }
        '''

        view_name = data["view_name"]
        job_name = data.get("job_name")
        job_detail = data.get("job_detail")

        user = data.get("user") if data.get("user") else ""
        command = cgi.escape(job_detail.get("command"))
        params = job_detail.get("params")
        param_xml = ""
        for param in params:
            name = param.get("name")
            default_value = param.get("default_value") if param.get("default_value") else ""
            param_xml += values.JOB_PARAM_XML % (name, default_value)
        param_xml += values.JOB_PARAM_XML % (values.USER_EMAIL, user)
        report_url = "http://agile.meiliworks.com/ci_mgr/report/result"
        if request:
            host = request.META.get("HTTP_HOST")
            report_url = "http://" + host + "/ci_mgr/report/result"
        if conf == "JOB_CONFIG_XML":
            param_xml += values.JOB_PARAM_XML % (values.JOB_RECORD_ID, "")
            conf_xml = values.JOB_CONFIG_XML % (param_xml, command, report_url)
        elif conf == "TRIGGER_JOB_CONF":
            svn = data.get("svn")
            conf_xml = values.TRIGGER_JOB_CONF % (param_xml, svn, command)
        elif conf == "TIMER_JOB_CONF":
            timer = data.get("timer")
            conf_xml = values.TIMER_JOB_CONF % (timer, command)
        else:
            return "no conf_xml match"
        j = jenkins.Jenkins(self._get_view_url(view_name), self.user, self.password)
        j.create_job(job_name, conf_xml)

    def get_job_config(self, name):
        job_url = "%s/job/%s/api/json?pretty=true" % (self.jenkins_url, name)
        ret = json.loads(public.get_data(job_url))
        return ret


def save_module(data):
    j = Jenkins()
    id = data.get("id")
    name = data.get("name")
    if id:
        mod = models.Module.objects.get(id=id)
    else:
        ret = j.create_view(name)
        if ret.get("status") == "fail":
            return ret
        mod, create = models.Module.objects.get_or_create(name=name)
        mod.name = data.get("name")
    mod.trunk = data.get("trunk")
    mod.branch = data.get("branch")
    mod.type = data.get("type")
    mod.save()
    return ret


def get_module_list():
    mod = models.Module.objects.all()
    ret = []
    for m in mod:
        tmp = model_to_dict(m)
        ret.append(tmp)
    return ret


def get_module_by_name(name):
    ret = {}
    mod = models.Module.objects.filter(name=name)
    if mod:
        ret = model_to_dict(mod[0])
    return ret


def get_module_by_id(id):
    ret = {}
    mod = models.Module.objects.filter(id=id)
    if mod:
        ret = model_to_dict(mod[0])
    return ret

def save_task_trigger_job(data):
    '''
    {
        "task_id":1,
        "svn_list":["http://svn.meilishuo.com/repos/snake/trunk/",],
        "user":"liliurd@meilishuo.com"
    }
    '''
    task_id = data.get("task_id")
    svn_list = data.get("svn_list")
    user_email = data.get("user") if data.get("user") else ""
    task = models.Task.objects.get(id=task_id)
    trigger_job = json.loads(task.trigger_job) if task.trigger_job else []

    j = Jenkins()
    module = models.Module.objects.get(id=task.module_id)
    job_svn = []
    for job in trigger_job:
        job_svn.append(job.get("svn"))
    svn_exits = []
    svn_new = []
    for svn in svn_list:
        if svn not in job_svn:
            job_name = "trigger-" + time.strftime("%y%m%d%H%M%S")
            param = {}
            param["view_name"] = module.name
            param["job_name"] = job_name
            param["user"] = user_email
            param["svn"] = svn
            param["job_detail"] = {}
            param["job_detail"]["command"] = 'python /home/work/AutoEnvironment/bin/svn_report.py "${svn}" "${task_id}"'
            param["job_detail"]["params"] = [
                {"name": "svn", "description": "", "default_value": svn},
                {"name": "task_id", "description": "", "default_value": task_id},
                ]
            j.create_view_job(param, "TRIGGER_JOB_CONF")
            svn_new.append({"svn": svn, "job_name": job_name, "task_id": task_id})
        else:
            svn_exits.append(svn)
    for job in trigger_job:
        if job.get("svn") in svn_exits:
            svn_new.append(job)
        else:
            try:
                j.delete_job(job.get("job_name"))
            except:
                pass
    task.trigger_job = json.dumps(svn_new)

    #创建task定时触发job
    timer = data.get("timer")
    old_timer = json.loads(task.timer if task.timer else "{}")

    if timer != old_timer.get("timer"):
        if old_timer.get("jenkins_name"):
            try:
                j.delete_job(old_timer.get("jenkins_name"))
            except:
                pass
            task.timer = "{}"
        if timer:
            job_name = "timer-" + time.strftime("%y%m%d%H%M%S")
            param = {}
            param["view_name"] = module.name
            param["job_name"] = job_name
            param["user"] = user_email
            param["timer"] = timer
            param["job_detail"] = {}
            param["job_detail"]["command"] = 'python /home/work/AutoEnvironment/bin/start_task.py "%s"' % task_id
            param["job_detail"]["params"] = []
            j.create_view_job(param, "TIMER_JOB_CONF")
            task.timer = json.dumps({"jenkins_name": job_name, "timer": timer})
    task.save()



def save_task(request):
    data = json.loads(request.body)
    id = data.get("id")
    if id:
        task = models.Task.objects.get(id=id)
    else:
        task = models.Task()
    task.name = data.get("name")
    task.module_id = data.get("module_id")
    task.desc = data.get("desc")
    task.type = data.get("type")
    task.user = public.get_user_mail(request)
    task.save()

    svn_list = data.get("svn_list") if data.get("svn_list") else []
    if not isinstance(svn_list, list):
        svn_list = [svn_list]
    param = {}
    param["task_id"] = task.id
    param["svn_list"] = svn_list
    param["timer"] = data.get("timer")
    param["user"] = public.get_user_mail(request)
    save_task_trigger_job(param)


def get_task(task_id):
    ret = {}
    task = models.Task.objects.filter(id=task_id)
    if task:
        ret = model_to_dict(task[0])
        ret["trigger_job"] = json.loads(ret.get("trigger_job")) if ret.get("trigger_job") else []
        ret["timer"] = json.loads(ret.get("timer")) if ret.get("timer") else {}
    return ret


def get_task_all():
    tasks = models.Task.objects.all()
    ret = []
    for task in tasks:
        tmp = model_to_dict(task)
        tmp["trigger_job"] = json.loads(tmp.get("trigger_job")) if tmp.get("trigger_job") else []
        ret.append(tmp)
    return ret


def get_task_list(module_id=None):
    ret = []
    if module_id:
        task = models.Task.objects.filter(module_id=module_id)
    else:
        task = models.Task.objects.all()
    for t in task:
        tmp = model_to_dict(t)
        tmp["trigger_job"] = json.loads(tmp.get("trigger_job")) if tmp.get("trigger_job") else []
        ret.append(tmp)
    return ret

def save_sub_task(request):
    data = json.loads(request.body)
    task_id = data.get("task_id") if data.get("task_id") else 0
    id = int(data.get("id")) if data.get("id") else 0
    pre_id = int(data.get("pre")) if data.get("pre") else 0
    is_start = int(data.get("is_start")) if data.get("is_start") else 0
    if not task_id:
        return u"task_id不存在"
    sub_tasks = models.SubTask.objects.filter(task_id=task_id)
    if id:
        sub_task = sub_tasks.get(id=id)
        if pre_id == id and id != 0:
            return u"不可以将自己设为前置子任务"
    else:
        sub_task = models.SubTask()

    if is_start != 0:
        sub_task.is_start = True
        sub_task.pre = 0
    else:
        sub_task.is_start = False
        sub_task.pre = pre_id
    sub_task.name = data.get("name")
    sub_task.task_id = task_id
    sub_task.type = data.get("type") if data.get("type") else 0
    sub_task.desc = data.get("desc")
    sub_task.user = public.get_user_mail(request)
    sub_task.save()
    sub_tasks.filter(next=sub_task.id).update(next=0)
    if pre_id and False == sub_task.is_start:
        sub_tasks.filter(id=pre_id).update(next=sub_task.id)
    if is_start:
        start_sub = sub_tasks.exclude(id=sub_task.id).filter(is_start=True)
        if start_sub:
            sub_task.next = start_sub[0].id
            sub_task.save()
        start_sub.update(pre=sub_task.id, is_start=False)

def set_sub_task_order(data):
    id = data.get("id")
    from_id = data.get("pre")
    to_id = data.get("next")
    is_start = data.get("is_start")
    sub_task = models.SubTask.objects.filter(id=id)
    if is_start:
        sub_task.update(is_start=int(is_start))
        models.SubTask.objects.filter(task_id=sub_task[0].task_id).exclude(id=id).update(is_start=False)
    if from_id:
        sub_task.update(pre=from_id)
        sub_task.update(is_start=False)
    if to_id:
        sub_task.update(next=to_id)
    else:
        sub_task.update(next=0)


def get_sub_task_all(task_id=None):
    if task_id:
        sub_tasks = models.SubTask.objects.filter(task_id=task_id)
    else:
        sub_tasks = models.SubTask.objects.all()

    ret = []
    for sub in sub_tasks:
        tmp = model_to_dict(sub)
        tmp["is_start"] = int(sub.is_start)
        ret.append(tmp)
    return ret


def get_sub_task_list(task_id):
    sub_tasks = models.SubTask.objects.filter(task_id=task_id)
    ret = {}
    ret["include"] = []
    ret["exclude"] = []
    sub_task = sub_tasks.filter(is_start=True)
    in_id = []
    if sub_task:
        sub = sub_task[0]
        in_id.append(sub.id)
        tmp = model_to_dict(sub)
        tmp["is_start"] = int(sub.is_start)
        ret["include"].append(tmp)
        try:
            i = 0
            while sub.next and i < 10:
                sub = sub_tasks.get(id=sub.next)
                in_id.append(sub.id)
                tmp = model_to_dict(sub)
                tmp["is_start"] = int(sub.is_start)
                ret["include"].append(tmp)
                i += 1
        except:
            pass
    out_sub = sub_tasks.exclude(id__in=in_id)
    for out in out_sub:
        tmp = model_to_dict(out)
        ret["exclude"].append(tmp)

    return ret


def get_sub_task_info(id):
    sub_task = models.SubTask.objects.get(id=id)
    ret = model_to_dict(sub_task)
    ret["is_start"] = int(sub_task.is_start)
    ret["createTime"] = public.datetime2str(sub_task.createTime)
    return ret


def bind_sub_task_job(sub_task_id, job_id_list):
    if not isinstance(job_id_list, list):
        job_id_list = [job_id_list]
    for job_id in job_id_list:
        job_set, create = models.JobSet.objects.get_or_create(subtask_id=sub_task_id, job_id=job_id)
        next_id = json.loads(job_set.next)
        if next_id:
            tmp = []
            for n_id in next_id:
                if n_id in job_id_list:
                    tmp.append(n_id)
            job_set.next = json.dumps(tmp)
            job_set.save()
    models.JobSet.objects.filter(subtask_id=sub_task_id).exclude(job_id__in=job_id_list).delete()


def set_sub_task_job_order(data):
    sub_task_id = data.get("sub_task_id")
    id = int(data.get("id")) if data.get("id") else 0
    is_start = int(data.get("is_start")) if data.get("is_start") else 0
    to_id_list = data.get("to_id_list", [])
    job_set = models.JobSet.objects.filter(subtask_id=sub_task_id)
    if not isinstance(to_id_list, list):
        to_id_list = [to_id_list]
    to_list = []
    for to_id in to_id_list:
        to_id = int(to_id)
        to_list.append(to_id)
    if id in to_list:
        return u"不能将自己设为自己的后置"

    if is_start:
        # 从已有的前置job中去掉
        for job in job_set:
            pre_next = json.loads(job.next)
            if id in pre_next:
                pre_next = list(set(pre_next).difference(set([id])))
                job.next = json.dumps(pre_next)
                job.save()
    job_set.filter(job_id=id).update(is_start=is_start, next=json.dumps(to_list))
    job_set.filter(job_id__in=to_list).update(is_start=False, next="[]")
    start_count = models.JobSet.objects.filter(subtask_id=sub_task_id, is_start=True).count()
    if start_count == 0:
        job_set.filter(job_id=id).update(is_start=True)


def get_sub_task_job_all(sub_task_id):
    jobset = models.JobSet.objects.filter(subtask_id=sub_task_id)
    jobs = models.Job.objects.all()
    ret = []
    for job in jobset:
        j = jobs.get(id=job.job_id)
        tmp = model_to_dict(j)
        tmp["job_detail"] = json.loads(j.job_detail)
        tmp["id"] = job.job_id
        tmp["next"] = json.loads(job.next)
        ret.append(tmp)
    return ret


def get_next_job(job, jobs):
    job_id = job.job_id
    j = jobs.get(id=job_id)
    tmp = model_to_dict(j)
    tmp["id"] = j.id
    tmp["job_detail"] = json.loads(j.job_detail)
    tmp["next_id"] = json.loads(job.next)
    tmp["next"] = []
    return tmp


def get_sub_task_job_list(sub_task_id):
    jobset = models.JobSet.objects.filter(subtask_id=sub_task_id)
    jobs = models.Job.objects.all()
    start_jobs = jobset.filter(is_start=True)
    ret = {}
    ret["jobs"] = []
    ret["deep"] = 0
    for job in start_jobs:
        tmp1 = get_next_job(job, jobs)
        job_tmp = jobset.filter(job_id__in=tmp1["next_id"])
        ret["deep"] = 1
        for job in job_tmp:
            tmp2 = get_next_job(job, jobs)
            job_tmp = jobset.filter(job_id__in=tmp2["next_id"])
            ret["deep"] = 2
            for job in job_tmp:
                tmp3 = get_next_job(job, jobs)
                job_tmp = jobset.filter(job_id__in=tmp3["next_id"])
                ret["deep"] = 3
                for job in job_tmp:
                    tmp4 = get_next_job(job, jobs)
                    job_tmp = jobset.filter(job_id__in=tmp4["next_id"])
                    ret["deep"] = 4
                    for job in job_tmp:
                        tmp5 = get_next_job(job, jobs)
                        job_tmp = jobset.filter(job_id__in=tmp5["next_id"])
                        ret["deep"] = 5
                        for job in job_tmp:
                            tmp6 = get_next_job(job, jobs)
                            job_tmp = jobset.filter(job_id__in=tmp6["next_id"])
                            ret["deep"] = 6
                            for job in job_tmp:
                                tmp7 = get_next_job(job, jobs)
                                job_tmp = jobset.filter(job_id__in=tmp7["next_id"])
                                ret["deep"] = 7
                                for job in job_tmp:
                                    tmp8 = get_next_job(job, jobs)
                                    job_tmp = jobset.filter(job_id__in=tmp8["next_id"])
                                    ret["deep"] = 8
                                    for job in job_tmp:
                                        tmp9 = get_next_job(job, jobs)
                                        job_tmp = jobset.filter(job_id__in=tmp9["next_id"])
                                        ret["deep"] = 9
                                        for job in job_tmp:
                                            tmp10 = get_next_job(job, jobs)
                                            ret["has_id"].append(tmp10["id"])
                                            ret["deep"] = 10
                                        tmp8["next"].append(tmp9)
                                    tmp7["next"].append(tmp8)
                                tmp6["next"].append(tmp7)
                            tmp5["next"].append(tmp6)
                        tmp4["next"].append(tmp5)
                    tmp3["next"].append(tmp4)
                tmp2["next"].append(tmp3)
            tmp1["next"].append(tmp2)
        ret["jobs"].append(tmp1)
    return ret


def save_module_job(request):
    '''
    {
        "module_id":1,
        "name":"test1",
        "type":1,
        "scene":"",
        "desc":"xxxx",
        "job_detail":{
            "description":"just a test",
            "command":"ls -l",
            "params":[
                {
                    "name":"branch_num",
                    "description":"just a test",
                    "default_value":"trunk"
                },
                {
                    "name":"version",
                    "description":"121212",
                    "default_value":""
                }
            ]
        }
    }
    '''
    data = json.loads(request.body)
    module_id = data.get("module_id")
    if not module_id:
        return None
    id = data.get("id")
    json_data = {}
    module = models.Module.objects.get(id=module_id)
    json_data["view_name"] = module.name
    json_data["job_name"] = "%s-%s" % (module.name, time.strftime("%y%m%d%H%M%S"))
    json_data["job_detail"] = data.get("job_detail")
    j = Jenkins()
    if id:
        job = models.Job.objects.get(id=id)
        old_name = job.jenkins_name
        if old_name:
            j.delete_job(old_name)
    else:
        job = models.Job()
    j.create_view_job(json_data, "JOB_CONFIG_XML", request)
    job.module_id = module_id
    job.name = data.get("name")
    job.jenkins_name = json_data.get("job_name")
    job.type = data.get("type")
    job.scene = data.get("scene")
    job.desc = data.get("desc")
    job.user = public.get_user_mail(request)
    job.job_detail = json.dumps(data.get("job_detail"))
    job.save()


def get_module_job_list(module_id):
    ret = []
    jobs = models.Job.objects.filter(module_id=module_id)
    for job in jobs:
        tmp = model_to_dict(job)
        tmp["createTime"] = public.datetime2str(job.createTime)
        tmp["job_detail"] = json.loads(job.job_detail)
        ret.append(tmp)
    return ret


def get_module_job(id):
    job = models.Job.objects.filter(id=id)
    ret = {}
    if job:
        job = job[0]
        ret = model_to_dict(job)
        ret["createTime"] = public.datetime2str(job.createTime)
        ret["job_detail"] = json.loads(job.job_detail)
    return ret


def get_task_record_status(task_record_id):
    record = models.TaskRecord.objects.get(id=task_record_id)
    return record.status


def get_task_status(task_id):
    task_record = models.TaskRecord.objects.filter(task_id=task_id)
    if task_record:
        task_record = task_record.latest("id")
        status = get_task_record_status(task_record.id)
    else:
        status = public.STATUS_UNKNOWN
    return status


def merge_task_record(data):
    task_id = data.get("task_id")
    page_current = data.get("page_current") if data.get("page_current") else 1
    ret = {}
    task_record = models.TaskRecord.objects.filter(task_id=task_id).order_by("-id")
    ret["page"] = public.paging_algorithm(len(task_record), page_current)
    if ret["page"]:
        task_record = task_record[ret["page"]["start"]:ret["page"]["end"]]
    ret["task"] = []
    for record in task_record:
        tmp_task = model_to_dict(record)
        tmp_task["name"] = json.loads(tmp_task["options"]).get("name")
        tmp_task["params"] = json.loads(tmp_task["params"]) if tmp_task["params"] else {}
        task_record_id = record.id
        tmp_task["sub_task"] = []
        sub_record = models.SubTaskRecord.objects.filter(task_record_id=task_record_id).order_by("id")
        for sub in sub_record:
            tmp_sub = model_to_dict(sub, exclude=["createTime", "runStartTime", "runEndTime"])
            tmp_sub["name"] = json.loads(tmp_sub["options"]).get("name")
            del tmp_sub["options"]
            job_record = models.JobRecord.objects.filter(task_record_id=task_record_id,
                                                         subtask_record_id=sub.id).order_by("id")
            tmp_sub["job"] = []
            for job in job_record:
                tmp_job = model_to_dict(job, exclude=["createTime", "runStartTime", "runEndTime"])
                tmp_job["options"] = json.loads(tmp_job["options"])
                tmp_job["name"] = tmp_job["options"].get("name")
                tmp_sub["job"].append(tmp_job)
            tmp_task["sub_task"].append(tmp_sub)
        ret["task"].append(tmp_task)
    return ret

def rm_job(id):
    count = models.JobSet.objects.filter(job_id=id).count()
    if count:
        return u"该job有子任务绑定，请先去掉绑定关系！"
    jobs = models.Job.objects.filter(id=id)
    if jobs:
        job = jobs[0]
        jenkins_name = job.jenkins_name
        if jenkins_name:
            j = Jenkins()
            j.delete_job(jenkins_name)
    jobs.delete()

def rm_sub_task(id):
    count = models.JobSet.objects.filter(subtask_id=id).count()
    if count:
        return u"该子任务已经绑定job，请先去掉绑定关系！"
    sub_tasks = models.SubTask.objects.filter(id=id)
    if sub_tasks:
        next_id = sub_tasks[0].next
        is_start = sub_tasks[0].is_start
        pre = models.SubTask.objects.filter(next=id)
        if next_id:
            pre.update(next=next_id)
            if is_start:
                models.SubTask.objects.filter(id=next_id).update(is_start=True)
        else:
            pre.update(next=0)
        sub_tasks.delete()

def rm_task(id):
    count = models.SubTask.objects.filter(task_id=id).count()
    if count:
        return u"改任务下含有子任务，请先删掉其子任务！"
    models.Task.objects.filter(id=id).delete()

# 以下主要跟job运行相关
def run_job(data):
    job_id = data.get("job_id")
    param = data.get("param")
    run_params = data.get("run_params")
    record_id = data.get("record_id")
    user = data.get("user")
    job = models.Job.objects.get(id=job_id)
    jenkins_name = job.jenkins_name
    params = json.loads(job.job_detail).get("params")
    params_dict = {}

    job_prarms = []
    if run_params:
        for run in run_params:
            if int(run.get("job_id")) == int(job_id):
                job_prarms = run.get("params")
                break
    if params:
        #手动触发传人的参数
        if job_prarms:
            for p in job_prarms:
                params_dict[p.get("name")] = p.get("value")
        else:
            for p in params:
                name = p.get("name")
                #job间的传参
                if param:
                    if name in param:
                        params_dict[name] = param[name]
                    else:
                        params_dict[name] = p.get("default_value")
                #否则使用默认值
                else:
                    params_dict[name] = p.get("default_value")

    params_dict[values.JOB_RECORD_ID] = record_id
    params_dict[values.USER_EMAIL] = user
    j = Jenkins()
    j.build_job(jenkins_name, params_dict)


def create_job_record(data):
    subtask_id = data.get("subtask_id")
    subtask_record_id = data.get("subtask_record_id")
    task_record_id = data.get("task_record_id")
    jobsets = models.JobSet.objects.filter(subtask_id=subtask_id, is_start=True)
    if len(jobsets) == 0:
        models.SubTaskRecord.objects.filter(id=subtask_record_id).update(status=public.STATUS_FAIL, runEndTime=datetime.now())
        models.TaskRecord.objects.filter(id=task_record_id).update(status=public.STATUS_FAIL, end_time=datetime.now())
    for jobset in jobsets:
        record = models.JobRecord()
        record.module_id = data.get("module_id")
        record.task_record_id = task_record_id
        record.subtask_record_id = data.get("subtask_record_id")
        record.jobset_id = jobset.id
        record.job_id = jobset.job_id
        record.subtask_record_id = subtask_record_id
        record.status = public.STATUS_RUNNING
        record.runStartTime = datetime.now()
        record.is_start = True
        record.options = json.dumps(model_to_dict(models.Job.objects.get(id=jobset.job_id)))
        record.save()
        param = {}
        param["job_id"] = jobset.job_id
        param["record_id"] = record.id
        param["user"] = data.get("user")
        param["run_params"] = data.get("run_params")
        run_job(param)


def create_sub_task_record(data):
    record = models.SubTaskRecord()
    record.module_id = data.get("module_id")
    record.task_id = data.get("task_id")
    record.task_record_id = data.get("task_record_id")
    record.subtask_id = data.get("subtask_id")
    record.user = data.get("user")
    record.status = public.STATUS_RUNNING
    record.runStartTime = datetime.now()
    record.options = data.get("options") if data.get("options") else "{}"
    record.save()
    data["subtask_record_id"] = record.id
    create_job_record(data)


def start_task(request):
    data = json.loads(request.body)
    task_id = data.get("task_id")
    sheet_id = data.get("sheet_id", "")
    run_type = data.get("run_type", public.RUN_TYPE_DEBUG)
    if not task_id:
        return "task_id is not exits!"
    task = models.Task.objects.get(id=task_id)
    subtask = models.SubTask.objects.filter(task_id=task_id, is_start=True)
    module_id = task.module_id
    task_record = models.TaskRecord()
    task_record.task_id = task_id
    task_record.module_id = module_id
    if len(subtask):
        task_record.status = public.STATUS_RUNNING
    else:
        task_record.status = public.STATUS_FAIL
    options = model_to_dict(task)
    options["other"] = data
    options["runner"] = public.get_user_mail(request)
    task_record.options = json.dumps(options)
    if run_type == public.RUN_TYPE_AUTO:
        task_record.sheet_id = data.get("sn")
    else:
        task_record.sheet_id = sheet_id
    task_record.run_type = run_type
    task_record.save()
    task_record_id = task_record.id
    for sub in subtask:
        param = {}
        param["task_record_id"] = task_record_id
        param["task_id"] = task_id
        param["module_id"] = module_id
        param["subtask_id"] = sub.id
        param["is_start"] = sub.is_start
        param["user"] = public.get_user_mail(request)
        param["options"] = json.dumps(model_to_dict(sub))
        param["run_params"] = data.get("run_params", [])
        create_sub_task_record(param)


def get_next_job_param(url, job_record_id):
    #传递参数格式为: NEXT_JOB_PARAM=key::value&&key1::value1
    params = {}
    ret = public.get_data(url)
    start_index = ret.rfind(public.JOB_PARAM)
    if start_index == -1:
        return params
    ret = ret[start_index:]
    end_index = ret.find("\n")
    param = public.JOB_PARAM + "="
    ret = ret[:end_index].strip().replace(" ", "").replace(param, "").split("&&")

    job_record = models.JobRecord.objects.get(id=job_record_id)
    task_record_id = job_record.task_record_id
    task_record = models.TaskRecord.objects.get(id=task_record_id)
    params = json.loads(task_record.params) if task_record.params else {}
    for r in ret:
        tmp = r.strip().split("::")
        if len(tmp) == 2:
            params[tmp[0]] = tmp[1]
    task_record.params = json.dumps(params)
    task_record.save()
    return params


def save_report_result(request):
    build_url = request.GET.get("build_url")
    job_record_id = request.GET.get("job_record_id")
    user_email = request.GET.get("user_email")
    json_url = build_url + "api/json?pretty=true"
    result_url = build_url + "consoleText"
    param = get_next_job_param(result_url, job_record_id)
    ret = json.loads(public.get_data(json_url))
    if ret.get("result") != "SUCCESS":
        status = public.STATUS_FAIL
    else:
        status = public.STATUS_PASS
    data = {"status": status, "build_url": build_url, "job_record_id": job_record_id, "user_email": user_email,
            "param": param}
    jenkins_update_status(data)


def check_task_record(task_record_id):
    task_record = models.TaskRecord.objects.filter(id=task_record_id)
    job_record = models.SubTaskRecord.objects.filter(task_record_id=task_record_id)
    run_num = job_record.filter(status=public.STATUS_RUNNING).count()
    fail_num = job_record.filter(status=public.STATUS_FAIL).count()
    if fail_num != 0:
        task_record.update(status=public.STATUS_FAIL, end_time=datetime.now())
    elif run_num != 0:
        task_record.update(status=public.STATUS_RUNNING, end_time=datetime.now())
    else:
        task_record.update(status=public.STATUS_PASS, end_time=datetime.now())


def check_sub_task_record(sub_task_record_id):
    sub_record = models.SubTaskRecord.objects.filter(id=sub_task_record_id)
    record = sub_record[0]
    subtask_id = record.subtask_id
    task_record_id = record.task_record_id
    sub_task = models.SubTask.objects.get(id=subtask_id)
    next_id = sub_task.next
    jobRecord = models.JobRecord.objects.filter(subtask_record_id=sub_task_record_id)
    run_num = jobRecord.filter(status=public.STATUS_RUNNING).count()
    fail_num = jobRecord.filter(status=public.STATUS_FAIL).count()
    if fail_num != 0:
        status = public.STATUS_FAIL
        sub_record.update(status=status, runEndTime=datetime.now())
    elif run_num != 0:
        status = public.STATUS_RUNNING
        sub_record.update(status=status, runEndTime=datetime.now())
    else:
        status = public.STATUS_PASS
        sub_record.update(status=status, runEndTime=datetime.now())
    if next_id and status != public.STATUS_RUNNING:
        param = {}
        param["task_record_id"] = task_record_id
        param["task_id"] = record.task_id
        param["module_id"] = record.module_id
        param["subtask_id"] = next_id
        param["is_start"] = False
        param["user"] = record.user if record.user else ""
        param["options"] = json.dumps(model_to_dict(models.SubTask.objects.get(id=next_id)))
        create_sub_task_record(param)
    else:
        check_task_record(task_record_id)


def jenkins_update_status(data):
    status = int(data.get("status"))
    job_record_id = data.get("job_record_id")
    user = data.get("user") if data.get("user") else ""
    job_record = models.JobRecord.objects.filter(id=job_record_id)
    if job_record:
        job = job_record[0]
        old_options = {}
        try:
            old_options = json.loads(job.options)
        except:
            pass
        old_options["result"] = data
        job_record.update(status=status, options=json.dumps(old_options), runEndTime=datetime.now())
        subtask_record_id = job.subtask_record_id
        if status != public.STATUS_PASS:
            models.SubTaskRecord.objects.filter(id=subtask_record_id).update(status=status, runEndTime=datetime.now())
            models.TaskRecord.objects.filter(id=job.task_record_id).update(status=status, end_time=datetime.now())
            return {"status": status}

        jobset = models.JobSet.objects.get(id=job.jobset_id)
        jobsets = models.JobSet.objects.filter(subtask_id=jobset.subtask_id)
        next_job = json.loads(jobset.next)
        if next_job:
            for j in next_job:
                js = jobsets.get(job_id=j)
                r = job
                r.id = None
                r.jobset_id = js.id
                r.job_id = j
                r.status = public.STATUS_RUNNING
                r.runStartTime = datetime.now()
                r.is_start = False
                r.param = json.dumps(data.get("param"))
                r.options = json.dumps(model_to_dict(models.Job.objects.get(id=j)))
                r.save()
                param = {}
                param["job_id"] = r.job_id
                param["record_id"] = r.id
                param["user"] = user
                param["param"] = data.get("param")
                run_job(param)
        else:
            check_sub_task_record(subtask_record_id)


def get_jobs_no_seq_by_sub_task_id(subtask_id):
    jobs = models.JobSet.objects.filter(subtask_id=subtask_id)
    ret = []
    for i in jobs:
        tmp = model_to_dict(i, fields=[], exclude=[])
        ret.append(tmp)
    return ret


def get_job_info_by_id(job_id):
    job_info = models.Job.objects.filter(id=job_id)
    if job_info:
        return model_to_dict(job_info[0], fields=[], exclude=[])
    else:
        return None


def get_job_set_by_job_id_sub_task_id(job_id, sub_task_id):
    job_info = models.JobSet.objects.filter(job_id=job_id, subtask_id=sub_task_id)
    if job_info:
        return model_to_dict(job_info[0], fields=[], exclude=[])
    else:
        return None

depth = 1

def recursion_scan(tree):
    for i in tree:
        i['children'] = i['next']
        if i['next'] != []:
            recursion_scan(i['next'])
        else:
            continue
    return tree


def get_latest_task_record(task_id):
    task_record = models.TaskRecord.objects.filter(task_id=task_id)
    ret = {}
    if task_record:
        task_record = task_record.latest("id")
        ret = model_to_dict(task_record)
        ret["start_time"] = public.datetime2str(task_record.start_time)
        ret["end_time"] = public.datetime2str(task_record.end_time)
        ret["options"] = json.loads(ret.get("options", "{}"))
        if "trigger_job" in ret["options"]:
            del ret["options"]["trigger_job"]
    return ret

def static_ci_task(task_id):
    task_record = models.TaskRecord.objects.filter(task_id=task_id).order_by("-id")[0:5]
    ret = {}
    ret["run_time"] = []
    ret["last_ci_result"] = public.STATUS_UNKNOWN
    total = 0
    pass_num = 0
    flag = 1
    for record in task_record:
        if flag == 1:
            ret["last_ci_result"] = record.status
            flag = 0
        run_time = time.mktime(record.end_time.timetuple()) - time.mktime(record.start_time.timetuple())
        ret["run_time"].append(run_time)
        total += 1
        if record.status == public.STATUS_PASS:
            pass_num += 1
    ret["success_rate"] = pass_num*1.0/total if total else 0.0
    return ret

def static_dashboard():
    data = {}
    data["latest"] = []
    modules = get_module_list()
    for module in modules:
        tmp = module
        tasks = get_task_list(module.get("id"))
        tmp["task_record"] = []
        for task in tasks:
            tmp["task_record"].append(get_latest_task_record(task.get("id")))
            if not task.get("trigger_job"):
                continue
            tmp["static"] = static_ci_task(task.get("id"))
        data["latest"].append(tmp)
    return data

def get_task_record_status(task_record_id):
    task = models.JobRecord.objects.filter(task_record_id=task_record_id)
    pass_num = task.filter(status__in=[public.STATUS_PASS, public.STATUS_MANUAL_PASS]).count()
    fail_num = task.filter(status=public.STATUS_FAIL).count()
    run_num = task.filter(status=public.STATUS_RUNNING).count()
    if fail_num > 0:
        status = public.STATUS_FAIL
    elif run_num > 0:
        status = public.STATUS_RUNNING
    elif pass_num > 0 :
        status = public.STATUS_PASS
    else:
        status = public.STATUS_RUNNING
    return status

def get_sub_task_record_status(subtask_record_id):
    sub = models.JobRecord.objects.filter(subtask_record_id=subtask_record_id)
    pass_num = sub.filter(status__in=[public.STATUS_PASS, public.STATUS_MANUAL_PASS]).count()
    fail_num = sub.filter(status=public.STATUS_FAIL).count()
    run_num = sub.filter(status=public.STATUS_RUNNING).count()
    if fail_num > 0:
        status = public.STATUS_FAIL
    elif run_num > 0:
        status = public.STATUS_RUNNING
    elif pass_num > 0 :
        status = public.STATUS_PASS
    else:
        status = public.STATUS_RUNNING
    return status

def save_job_reason(request):
    data = json.loads(request.body)
    id = data.get("id")
    reason = data.get("reason")
    fail_type = data.get("fail_type")
    status = data.get("status")
    user = public.get_user_mail(request)
    if status:
        models.JobRecord.objects.filter(id=id).update(reason=reason, user=user, fail_type=fail_type, status=status)
        job_record = models.JobRecord.objects.get(id=id)
        task_status = get_task_record_status(job_record.task_record_id)
        sub_status = get_sub_task_record_status(job_record.subtask_record_id)
        models.TaskRecord.objects.filter(id=job_record.task_record_id).update(status=task_status)
        models.SubTaskRecord.objects.filter(id=job_record.subtask_record_id).update(status=sub_status)
    else:
        models.JobRecord.objects.filter(id=id).update(reason=reason, user=user, fail_type=fail_type)

def get_fail_type(id=None):
    if not id:
        fail = models.FailType.objects.all()
        ret = []
        for f in fail:
            ret.append(model_to_dict(f))
    else:
        fail = models.FailType.objects.get(id=id)
        ret = model_to_dict(fail)
    return ret

def manual_task_config(task_id):
    sub_task = models.SubTask.objects.filter(task_id=task_id, is_start=True)
    ret = []
    if sub_task:
        sub = sub_task[0]
        subtask_id =  sub.id
        job_sets = models.JobSet.objects.filter(subtask_id=subtask_id, is_start=True)
        for job_set in job_sets:
            job_id = job_set.job_id
            job = models.Job.objects.get(id=job_id)
            tmp = model_to_dict(job)
            tmp["job_detail"] = json.loads(job.job_detail)
            ret.append(tmp)
    return ret
