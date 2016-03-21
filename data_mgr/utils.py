# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''
import logging
import json
import os
import time
import uuid
import datetime
import urllib2,cookielib
import urllib
from django.core import serializers
from django.db.models import Q,F
from django.conf import settings
from django.forms.models import model_to_dict
import public
import models
import commands
import requests
import subprocess

from web_mgr import utils as web_utils

logger = logging.getLogger("web_site.data_mgr.util")



def make_uuid():
    return str(uuid.uuid1().int >> 64)


def save_pic(url):
    try:
        url = url.strip()
        target = "%s/%s/%s" % (time.strftime("%Y"), time.strftime("%m"), time.strftime("%d"))

        media_dir = os.path.join(settings.MEDIA_ROOT, target)
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        f_name = "%s.jpg" % make_uuid()
        path = os.path.join(media_dir, f_name)

        data = urllib.urlopen(url).read()
        f = file(path, "wb")
        f.write(data)
        f.close()

        media_url = "%s%s/%s" %(settings.MEDIA_URL, target, f_name)
    except:
        media_url = url

    return media_url


def save_dashboard(data):
    _type = data.get("type")
    env = data.get("env")
    scene = data.get("scene")
    runStartTime = public.time2datetime(data.get("runStartTime"))
    runEndTime = public.time2datetime(data.get("runEndTime"))
    interface = data.get("interface")
    options = data.get("data")
    err = None
    if env:
        dash = models.Dashboard()
        dash.type = _type
        dash.env = env
        dash.scene = scene
        dash.runStartTime = runStartTime
        dash.runEndTime = runEndTime
        dash.interface = interface

        if "pic" in options:
            url = options.get("pic")
            options["pic"] = save_pic(url)


        if "cpuPic" in options:
            url = options.get("cpuPic")
            options["cpuPic"] = save_pic(url)

        if "trafficPic" in options:
            url = options.get("trafficPic")
            options["trafficPic"] = save_pic(url)

        dash.options = json.dumps(options)
        dash.save()
    else:
        err = u"post数据有误!"
    return err


def get_dashboard(data, num=30, reverse=False):
    env = data.get("env")
    _type = data.get("type")
    scene = data.get("scene")
    start = data.get("start")
    end = data.get("end")
    interface = data.get("interface")
    interface_type = data.get("interface_type")

    q = Q(env=env)
    if _type:
        q &= Q(type=_type)
    if scene and _type != public.TYPE_TIME:
        q &= Q(scene=scene)
    if interface and interface != "all":
        q &= Q(interface=interface)
    if start:
        q &= Q(runEndTime__gte=public.str2datetime(start, "%Y-%m-%d"))
    if end:
        q &= Q(runEndTime__lte=public.str2datetime(end, "%Y-%m-%d")+datetime.timedelta(days=1))

    if num:
        dashboard = models.Dashboard.objects.filter(q).order_by('-runEndTime')[:num]
    else:
        dashboard = models.Dashboard.objects.filter(q).order_by('-runEndTime')

    case_list = []
    cases = json.loads(serializers.serialize('json', dashboard, fields=("env", "type", "scene", "interface",
                                                                     "runStartTime", "runEndTime", "options")))
    its = models.Interface.objects.filter(is_promotion=False)
    for c in cases:
        item = c['fields']
        item["options"] = json.loads(item.get("options", "{}"))
        item["runStartTime"] = item.get("runStartTime").replace("T", " ").split(" ")[0]
        item["runEndTime"] = item.get("runEndTime").replace("T", " ").split(" ")[0]
        item["type_alias"] = public.TYPE_DICT.get(item["type"])
        try:
            it = its.get(id=int(item["interface"]))
            item["desc"] = it.desc
            item["interface_type"] = it.type
            item["path"] = it.path
            if interface_type and interface_type != "all" and item["interface_type"] != interface_type:
                continue
        except:
            pass
        case_list.append(item)
    if reverse:
        case_list.reverse()
    return case_list


def get_dashboard_info(data, num=30, reverse=True):
    if data.get("type") == public.TYPE_CPU:
        data["unit_name"] = u"占用率"
        data["unit"] = "%"
    elif data.get("type") == public.TYPE_MEMORY:
        data["unit_name"] = u"字节"
        data["unit"] = "Byte"
    elif data.get("type") == public.TYPE_POWER:
        data["unit_name"] = u"cpu的tick数"
        data["unit"] = "tick"
    elif data.get("type") == public.TYPE_TRAFFIC:
        data["unit_name"] = u"兆"
        data["unit"] = "MB"
    elif data.get("type") == public.TYPE_TIME:
        data["unit_name"] = u"秒"
        data["unit"] = "s"
    else:
        data["unit_name"] = u""
        data["unit"] = ""
    ret = get_dashboard(data, num=num, reverse=reverse)
    categories = []
    series = []
    _max = []
    _min = []
    _avg = []
    _tx = []
    _rx = []
    _tps = []
    _error = []
    _cpu = []
    _main_time = []
    _install_time = []
    _welcome_time = []
    for r in ret:
        categories.append(r.get("runEndTime"))
        options = r.get("options", {})
        if options.get("max") is not None:
            _max.append(options.get("max"))
        if options.get("avg") is not None:
            _avg.append(options.get("avg"))
        if options.get("min") is not None:
            _min.append(options.get("min"))
        if options.get("tx") is not None:
            _tx.append(float(options.get("tx"))/1024/1024)
        if options.get("rx") is not None:
            _rx.append(float(options.get("rx"))/1024/1024)
        if options.get("tps") is not None:
            _tps.append(options.get("tps"))
        if options.get("error") is not None:
            _error.append(options.get("error"))
        if options.get("cpu") is not None:
            _cpu.append(options.get("cpu"))
        if options.get("main_time") is not None:
            _main_time.append(options.get("main_time"))
        if options.get("install_time") is not None:
            _install_time.append(options.get("install_time"))
        if options.get("welcome_time") is not None:
            _welcome_time.append(options.get("welcome_time"))
    if _max:
        tmp = {}
        tmp["name"] = u"最大值"
        tmp["data"] = _max
        series.append(tmp)
    if _avg:
        tmp = {}
        tmp["name"] = u"平均值"
        tmp["data"] = _avg
        series.append(tmp)
    if _min:
        tmp = {}
        tmp["name"] = u"最小值"
        tmp["data"] = _min
        series.append(tmp)
    if _tx:
        tmp = {}
        tmp["index"] = 1
        tmp["name"] = u"上行(MB)"
        tmp["data"] = _tx
        series.append(tmp)
    if _rx:
        tmp = {}
        tmp["index"] = 1
        tmp["name"] = u"下行(MB)"
        tmp["data"] = _rx
        series.append(tmp)
    if _tps:
        tmp = {}
        tmp["index"] = 2
        tmp["name"] = u"tps"
        tmp["data"] = _tps
        series.append(tmp)
    if _error:
        tmp = {}
        tmp["index"] = 3
        tmp["name"] = u"error"
        tmp["data"] = _error
        series.append(tmp)
    if _cpu:
        tmp = {}
        tmp["index"] = 4
        tmp["name"] = u"cpu"
        tmp["data"] = _cpu
        series.append(tmp)
    if _main_time:
        tmp = {}
        tmp["name"] = u"首页启动时间"
        tmp["data"] = _main_time
        series.append(tmp)
    if _install_time:
        tmp = {}
        tmp["name"] = u"安装需要时间"
        tmp["data"] = _install_time
        series.append(tmp)
    if _welcome_time:
        tmp = {}
        tmp["name"] = u"欢迎页启动时间"
        tmp["data"] = _welcome_time
        series.append(tmp)

    data["categories"] = categories
    data["series"] = series

    return data


def get_interface_info(data={}, is_promotion=False):
    _type = data.get("interface_type")
    its = models.Interface.objects.filter(is_promotion=is_promotion)
    if _type and _type != "all":
        interface = its.filter(type=_type)
    else:
        interface = its
    ret = []
    for i in interface:
        tmp = {}
        tmp["id"] = i.id
        tmp["desc"] = i.desc
        tmp["type"] = i.type
        tmp["path"] = i.path
        tmp["is_promotion"] = i.is_promotion
        ret.append(tmp)
    return ret


def check_mob(data):
    ret = get_dashboard(data, 11)
    status = public.LOWER_STATUS_SUCCESS
    if len(ret) > 1:
        latest = ret[0].get("options", {}).get("avg", 0.0)
        avg_sum = 0.0
        total = 0.0
        for r in ret[1:]:
            avg_sum += float(r.get("options", {}).get("avg", 0.0))
            total += 1
        avg = 0.0
        if avg_sum and total:
            avg = avg_sum/total
        if avg:
            avg = (latest - avg)/avg
        if avg > public.PERCENT:
            status = public.LOWER_STATUS_FAIL
    return status


def static_mob():
    data = []
    env = public.ENV_MOB
    for t in public.TYPE_LIST:
        d = {}
        d["type"] = t
        d["type_alias"] = public.TYPE_DICT.get(t)
        for s in public.SCENE_LIST:
            tmp = {}
            tmp["env"] = env
            tmp["type"] = t
            tmp["scene"] = s
            ret = check_mob(tmp)
            d[s] = ret
        data.append(d)
    return data


def check_newlab(data):
    ret = get_dashboard(data, 11)
    status = public.LOWER_STATUS_SUCCESS
    latest = None
    if len(ret) > 1:
        latest = ret[0]
        error = latest.get("options", {}).get("error", 0.0)
        tps = latest.get("options", {}).get("tps", 0.0)
        if error:
            status = public.LOWER_STATUS_FAIL
            return status, latest
        tps_sum = 0.0
        total = 0.0
        for r in ret[1:]:
            tps_sum += r.get("options", {}).get("tps", 0.0)
            total += 1
        avg = 0.0
        if tps_sum and total:
            avg = tps_sum/total
        if avg:
            r = (avg - tps)/avg
        if r > public.PERCENT:
            status = public.LOWER_STATUS_FAIL

    return status, latest


def static_newlab(data={}):
    env = public.ENV_NEWLAB
    info = get_interface_info(data)
    hot = 0
    web = 0
    fail_hot = 0
    fail_web = 0
    data = {}
    data["fail_list"] = []
    data["pass_list"] = []
    for d in info:
        if d.get("type") == public.INTERFACE_TYPE_HOT:
            hot += 1
        elif d.get("type") == public.INTERFACE_TYPE_WEB:
            web += 1

        tmp = {}
        tmp["env"] = env
        tmp["interface"] = d.get("id")
        tmp["desc"] = d.get("desc")
        ret, latest = check_newlab(tmp)
        if ret == public.LOWER_STATUS_FAIL:
            if d.get("type") == public.INTERFACE_TYPE_HOT:
                fail_hot += 1
            else:
                fail_web += 1
            data["fail_list"].append(latest)
        else:
            data["pass_list"].append(latest)

    data[public.INTERFACE_TYPE_HOT] = hot
    data[public.INTERFACE_TYPE_WEB] = web
    data["fail_hot"] = fail_hot
    data["fail_web"] = fail_web
    data["fail"] = fail_hot + fail_web
    return data


def save_promotion_record(data):
    promotion = data.get("promotion")
    interface = data.get("interface")
    index = data.get("index")
    description = data.get("description")
    start = public.time2datetime(data.get("start"))
    end = public.time2datetime(data.get("end"))
    options = data.get("data")
    err = None
    if promotion and interface and index:
        record = models.PromotionRecord()
        record.promotion = promotion
        record.interface = interface
        record.index = index
        record.description = description
        record.start = start
        record.end = end
        record.options = json.dumps(options)
        record.save()
    else:
        err = u"post数据有误"
    return err


def get_promotion(p_id=None):
    if p_id and p_id != "all":
        promotion = models.Promotion.objects.filter(id=int(p_id))
    else:
        promotion = models.Promotion.objects.all()
    data = []
    for prom in promotion:
        tmp = {}
        tmp["id"] = prom.id
        tmp["desc"] = prom.desc
        tmp["module"] = prom.module
        data.append(tmp)
    return data


def get_promotion_record(data={}):
    p_id = data.get("promotion")
    promotions = get_promotion(p_id)
    interfaces = get_interface_info(is_promotion=True)
    data = []
    for pro in promotions:
        records = models.PromotionRecord.objects.filter(promotion=str(pro.get("id")))
        tmp = {}
        tmp["id"] = pro.get("id")
        tmp["desc"] = pro.get("desc")
        tmp["interface"] = []
        tmp["interface_num"] = 0
        if records:
            for itf in interfaces:
                itf_dict = {}
                itf_dict["id"] = itf.get("id")
                itf_dict["desc"] = itf.get("desc")
                itf_dict["detail"] = []
                itf_dict["detail_num"] = 0
                record = records.filter(interface=str(itf.get("id")))
                for r in record:
                    detail = {}
                    detail["index"] = r.index
                    detail["desc"] = r.description
                    detail["end"] = public.datetime2str(r.end)
                    detail["options"] = json.loads(r.options)
                    itf_dict["detail"].append(detail)
                if itf_dict["detail"]:
                    itf_dict["detail_num"] = len(itf_dict["detail"])
                    tmp["interface"].append(itf_dict)
        if tmp["interface"]:
            tmp["interface_num"] = len(tmp["interface"])
            data.append(tmp)
    return data


def save_svn_history(data):
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    module_list = data.get("moduleEntityList", [])
    for module in module_list:
        modify = module.get("lineModifiedCount")
        name = module.get("moduleName")
        m = models.SvnHistory.objects.filter(module=name, create__gte=now)
        if len(m):
            m.delete()
        m = models.SvnHistory()
        m.module = name
        m.modify = int(modify)
        m.options = json.dumps(module)
        m.save()


def get_svn_history_test(data={}):
    logger.debug("get svn test")
    create = data.get("create")
    module = data.get("module")
    if not create:
        create = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)
    q = Q(create__gte=start) & Q(create__lt=end)
    if module and module != "all":
        q &= Q(module=module)

    ret = {}
    svn = models.SvnHistory.objects.filter(q)
    total = 0
    ret["detail"] = []
    ret["create"] = create
    ret["module"] = module
    for s in svn:
        tmp = {}
        tmp["id"] = s.id
        tmp["module"] = s.module
        tmp["create"] = public.datetime2str(s.create, "%Y-%m-%d")
        tmp["modify"] = s.modify
        tmp_options = json.loads(s.options)
        for commitlist in tmp_options['svnCommitList']:
            commitlist['modifiedFileUrl'] = []
            for filelist in commitlist['modifiedFileList']:
                #filelist['url'] = "http://svn.meilishuo.com/repos" + filelist.split(" ")[-1]
                #filelist['type'] = filelist.split(" ")[0]
                commitlist['modifiedFileUrl'].append("http://svn.meilishuo.com/repos" + filelist.split(" ")[-1])

        #tmp["options"] = json.loads(s.options)
        tmp["options"] = tmp_options

        total += tmp["modify"]
        ret["detail"].append(tmp)
    ret["total"] = total
    return ret


"""
#liujichao
def get_svn_history_test(data={}):
    # changed by yecheng
    TIMESTAMP="%Y%m%d%H%M%S"
    logger.debug("get svn test")
    module = data.get("module")
    end = public.str2datetime(data.get("end"), TIMESTAMP)

    if data.get("start") == None:
        start = time.strftime(TIMESTAMP , time.localtime(time.time()))
        start = public.str2datetime(start, TIMESTAMP)
        start = start - datetime.timedelta(days=1)

    else:
        start = public.str2datetime(data.get("start"), TIMESTAMP)

    create = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    #if not create:
    #    create = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    #start = public.str2datetime(create, "%Y-%m-%d")
    #end = start + datetime.timedelta(days=1)
    q = Q(create__gte=start) & Q(create__lt=end)
    if module and module != "all":
        q &= Q(module=module)
    print q

    ret = {}
    svn = models.SvnHistory.objects.filter(q)
    print len(svn)

    total = 0
    ret["detail"] = []
    ret["create"] = create
    ret["module"] = module
    for s in svn:
        tmp = {}
        tmp["id"] = s.id
        tmp["module"] = s.module
        tmp["create"] = public.datetime2str(s.create, "%Y-%m-%d")
        tmp["modify"] = s.modify
        tmp_options = json.loads(s.options)
        for commitlist in tmp_options['svnCommitList']:
            commitlist['modifiedFileUrl'] = []
            for filelist in commitlist['modifiedFileList']:
                #filelist['url'] = "http://svn.meilishuo.com/repos" + filelist.split(" ")[-1]
                #filelist['type'] = filelist.split(" ")[0]
                commitlist['modifiedFileUrl'].append("http://svn.meilishuo.com/repos" + filelist.split(" ")[-1])

        #tmp["options"] = json.loads(s.options)
        tmp["options"] = tmp_options

        total += tmp["modify"]
        ret["detail"].append(tmp)
    ret["total"] = total
    return ret
"""

#liujichao
def get_auto_report(data={}):
    create = data.get("create")
    module = data.get("module")
    if not create:
        create = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)
    q = Q(time__gte=start) & Q(time__lt=end)
    if module and module != "all":
        q &= Q(module=module)
    ret = []
    auto = models.AutoReport.objects.filter(q)
    for index in auto:
        tmp = {}
        tmp["id"] = index.id
        tmp["time"] = public.datetime2str(index.time)
        tmp["jsonString"] = json.loads(index.jsonString)
        ret.append(tmp)
    return ret

def get_push_status(data={}):

    create = data.get("create")
    module = data.get("module")
    if not create:
        create = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)
    q = Q(time__gte=start) & Q(time__lt=end)
    if module and module != "all":
        q &= Q(module=module)
    ret = []
    auto = models.AutoReport_pushStatus.objects.filter(time__gt=start)
    for index in auto:
        tmp = {}
        tmp["id"] = index.id
        tmp["time"] = public.datetime2str(index.time)
        tmp["jsonString"] = json.loads(index.jsonString)
        ret.append(tmp)
    return ret


def save_get_report(data):
    """
    liujichao
    存储autoreport 数据
    """
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    m = models.AutoReport.objects.filter(time__gte=now)
    if len(m):
        m.delete()
    m = models.AutoReport()
    m.jsonString = json.dumps(data)
    m.save()

def save_push_status():
    """
    liujichao
    存储上线状态 数据
    """
    userMainUrl = "http://syspush.meilishuo.com/opssys/index.php/Marklog/getLook";
    req = urllib2.Request(userMainUrl);
    resp = urllib2.urlopen(req);
    respHtml = json.loads(resp.read());
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    m = models.AutoReport_pushStatus.objects.filter(time__gte=now)
    if len(m):
        m.delete()
    m = models.AutoReport_pushStatus()
    m.jsonString = json.dumps(respHtml)
    m.save()

def save_release_plan(data):
    """
    liujichao
    存储发布计划数据,解析发布计划网页
    """
    from bs4 import BeautifulSoup
    task_id=data.get("task_id")
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    now_role_cursor=data.get("now_role_cursor")
    logger.debug("task_id : " + task_id)
    logger.debug("task_id : " + now_role_cursor)

    url = "http://sys-request.meilishuo.com/workflow/index.php/WFPakRequest/readTask?task_id="+task_id+"&now_role_cursor="+now_role_cursor
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    tmpNo = u'新增测试发布计划（不需要测试）'
    tmp = u'新增测试发布计划（需要测试）'
    for p in soup.find_all('p'):
        if p.text.strip() == tmp or p.text.strip() == tmpNo:
             for a in p.next_sibling.findAll("tr")[1:100]:
                 s=models.Push_data()
                 b =  a.findAll("td")
                 if (b):
                     s.time=now
                     s.url=url
                     s.releaseModel= b[0].text.strip()
                     s.content = b[1].text.strip()
                     s.product_director = b[3].text
                     s.develop_director = b[4].text
                     s.save()


def get_release_plan(data):
    """
    liujichao
    取出发布计划数据
    """
    create = data.get("create")
    module = data.get("module")
    if not create:
        create = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)
    q = Q(time__gte=start) & Q(time__lt=end)
    if module and module != "all":
        q &= Q(module=module)
    ret = []
    auto = models.Push_data.objects.filter(time__gt=start)
    for index in auto:
        tmp = {}
        tmp["id"] = index.id
        tmp["releaseModel"] = index.releaseModel
        tmp["develop_director"] = index.develop_director
        ret.append(tmp)
    return ret

def timestamp_datetime(value):
    """
    时间戳转换
    """
    format = '%Y-%m-%d'
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt

def save_auto_jenkins(data):
    """
    jichaoliu
    触发 jenkins  job
    """
    url ='http://jenkins.meiliworks.com/login?from=%2F'
    data = {'j_username':'jichaoliu','j_password':'ljc874765730','from':'/view/PC-Auto/view/Newlab/job/newlab-InterfaceAuto/','json':"{'j_username': 'jichaoliu', 'j_password': 'ljc874765730', 'remember_me': false, 'from': '/view/PC-Auto/view/Newlab/job/newlab-InterfaceAuto/'}",'Submit':'登录'}
    cookieJar=cookielib.CookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    urllib2.install_opener(opener);
    f = urllib2.urlopen(url,data = urllib.urlencode(data))
    cook = ""
    for ck in cookieJar:
            if ck.name == "JSESSIONID":
                    cook = ck.value
    cmd="curl 'http://jenkins.meiliworks.com/job/GuangZhou/build' -H 'Cookie: ACEGI_SECURITY_HASHED_REMEMBER_ME_COOKIE='amljaGFvbGl1OjE0MzMxNDcyMzcwNzM6OTA0ZmIxNGNmNDE5ZGE4NzhjOTA3M2RiMjVkYjFmMGZhMTY2NjliZDZkNTgwMTExZmVjMmVlZGM3ZGUyNDQ5OA=='; JSESSIONID='+cook+'; screenResolution=1920x1080' -H 'Origin: http://jenkins.meiliworks.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://jenkins.meiliworks.com/job/GZSmoke/build' -H 'Connection: keep-alive' --data 'json=%7B%7D' --compressed"
    cmd2="curl 'http://jenkins.meiliworks.com/job/Beijing/build' -H 'Cookie: ACEGI_SECURITY_HASHED_REMEMBER_ME_COOKIE='amljaGFvbGl1OjE0MzMxNDcyMzcwNzM6OTA0ZmIxNGNmNDE5ZGE4NzhjOTA3M2RiMjVkYjFmMGZhMTY2NjliZDZkNTgwMTExZmVjMmVlZGM3ZGUyNDQ5OA=='; JSESSIONID='+cook+'; screenResolution=1920x1080' -H 'Origin: http://jenkins.meiliworks.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://jenkins.meiliworks.com/job/GZSmoke/build' -H 'Connection: keep-alive' --data 'json=%7B%7D' --compressed"

    os.system(cmd)
    os.system(cmd2)

def get_package_status(data):
    """
    jichaoliu
    """
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    m =models.Package_status.objects.filter(time__gte=now)
    a=1
    b=2
    for i in m:
        if int(i.status) == 2:
            a=2
        elif int(i.status) == 1:
            b=1
    if a == 2 and b == 2:
        # web_mgr.views.save_auto_jenkins(data)
        save_auto_jenkins(data)

def save_package_status(data):
    """
    liujichao
    存储包上线状态 数据
    """
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    m = models.Package_status.objects.filter(time__gte=now)
    if len(m):
        m.delete()
    data_json = json.loads(data.get("addData_reason"))
    for tmp in data_json.keys():
        if "BJ" in tmp or "DFZ" in tmp or "GZ" in tmp:
            m = models.Package_status()
            m.package= tmp
            m.time = now
            m.status = data_json[tmp]
            m.save()
    get_package_status(data)

def get_goback_information(data):
    """
    liujichao
    取出回归状态信息
    """
    create = data.get("create")
    module = data.get("module")
    if not create:
        create = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)
    q = Q(time__gte=start) & Q(time__lt=end)
    if module and module != "all":
        q &= Q(module=module)
    s=models.StatusBack.objects.filter(q)
    ret = []
    for index in s:
        tmp = {}
        tmp["id"] = index.id
        tmp["project"] = index.project
        tmp["success"] = index.success
        ret.append(tmp)
    return ret

def save_goback_information():
    """
    liujichao
    存储回归状态信息
    """
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    create = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    start = public.str2datetime(create, "%Y-%m-%d")
    end = start + datetime.timedelta(days=1)

    q = Q(time__gte=start) & Q(time__lt=end)
    s=models.StatusBack.objects.filter(q)
    if len(s):
        s.delete()
    bj = ('BJ-InterfaceAuto','BeijingSmoke','BJ-PageCheck','ShopUIAutoTest')
    gz = ('GZ-InterfaceAuto','GZSmoke','GZ-PageCheck')
    ret = [bj,gz]
    # modified by : yechengzhou
    for z in ret:
        for i in z:
            url = "http://jenkins.meiliworks.com/job/"+i+"/lastBuild/api/python?pretty=true"
            result_dic = eval(urllib2.urlopen(url).read())
            dt = timestamp_datetime(int(str(result_dic['timestamp'])[0:10]))
            a=time.strftime( '%Y-%m-%d', time.gmtime( time.time() ) )
            if dt >= a:
                m=models.StatusBack()
                m.time = dt
                m.project = i
                m.success = result_dic['result']
                m.save()


def get_newlab_jenkinsjob():
    """
    :author: yechengzhou
    :return: all newlab jobs
    """
    """
    newlabapi = "http://jenkins.meiliworks.com/view/NEWLAB/api/python?pretty=true"
    result_dict = eval(urllib2.urlopen(newlabapi).read())
    jobs = result_dict['jobs']
    new_job_list = [] # dict list
    for j in jobs:
        this_dict = {}
        this_dict['name'] = j['name']
        this_dict['url'] = j['url']
        this_dict['status'] = j['color']
        # get last build
        job_detail = eval(urllib2.urlopen(this_dict['url'] + "api/python?pretty=true").read())
        this_dict['lastCompletedBuild'] = job_detail['builds']['lastCompletedBuild'][0]['number']
        for i in range(len(job_detail['builds'])):
            job_detail['builds']['lastSuccessfulBuild']
        this_dict['lastSuccess'] = job_detail['builds']['lastSuccessfulBuild']['number']
        this_dict['lastFailedBuild'] = job_detail['builds']['lastFailedBuild']['number']

        new_job_list.append(this_dict)
    return new_job_list
"""
    pass

def get_job_build_detail(jobname, build):
    url = "http://jenkins.meiliworks.com/job/" + jobname + "/" + build + "/api/python?pretty=true"
    job_build_detail = eval(urllib2.urlopen(url).read())
    return job_build_detail

def save_sealed_info(data):
    """
    :author: yechengzhou
    :param data: list of dict
    :return: err msg
    """
    ret_list = data

    if len(ret_list) == 0:
        return u"post信息有误"

    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # check if today's info already in db
    s = models.VersionDiff.objects.filter(day=today)
    if len(s):
        s.delete()

    for i in ret_list:
        record = models.VersionDiff()
        record.module = i['module']
        record.sealed = i['sealed']
        record.newlab = i['newlab']
        record.day = today
        record.save()
    return None



def get_sealed_info(day=None):
    """
    :author: yechengzhou
    :param day: 希望得到哪天的信息
    :return: json
    """
    if day==None:  # 无参数取今天
        day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    s = models.VersionDiff.objects.filter(day=day).exclude(newlab=F("sealed"))
    ret = []
    for i in s:
        tmp = {}
        tmp['module'] = i.module
        tmp['sealed'] = i.sealed
        tmp['newlab'] = i.newlab
        tmp['day'] = i.day
        ret.append(tmp)

    return ret


def get_sealdiffonline(day=None):
    """
    :author: yechengzhou
    :param day: 希望得到哪天的信息
    :return: json
    """

    if day==None:  # 无参数取今天
        day = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 获取上线信息, 实时
    userMainUrl = "http://syspush.meilishuo.com/opssys/index.php/Marklog/getLook"
    req = urllib2.Request(userMainUrl)
    resp = urllib2.urlopen(req).read()
    if len(resp) == 0 or type(eval(resp)) == type([]):
        return 1 #上线信息不存在

    online_dict = eval(resp)
    #respHtml = json.loads(resp.read());
    #print respHtml

    #return respHtml
    # 整理下信息
    online_list = []
    for k,v in online_dict.iteritems():
        tmp_dict = {}
        this_v = v['version']
        if this_v.find("RB") == 0:
            this_m = this_v[3:this_v.find('2')-1]
        else:
            this_m = this_v[:this_v.find('2')-1]
        tmp_dict['version'] = this_v
        tmp_dict['module'] = this_m.capitalize()
        tmp_dict['project'] = k
        tmp_dict['endflag'] = v['endflag']
        tmp_dict['updated_at'] = v['updated_at']
        online_list.append(tmp_dict)

    # 获取newlab信息并且对比
    s = models.VersionDiff.objects.filter(day=day)
    diff_ret = []
    for i in s:
        for j in online_list:
            if j['module'] == i.module:
                # 这个模块今天有上线 检查newlab版本与上线版本
                if j['version'] != i.newlab:
                    j['newlab'] = i.newlab
                    j['sealed'] = i.sealed
                    j['day'] = i.day
                    diff_ret.append(j)
    return diff_ret


def get_online_info():

    # 获取上线信息, 实时
    userMainUrl = "http://syspush.meilishuo.com/opssys/index.php/Marklog/getLook"
    req = urllib2.Request(userMainUrl)
    resp = urllib2.urlopen(req).read()
    if len(resp) == 0 or type(eval(resp)) == type([]):
        return False #上线信息不存在

    online_dict = eval(resp)
    #respHtml = json.loads(resp.read());
    #print respHtml

    #return respHtml
    # 整理下信息
    ret = {}
    for k,v in online_dict.iteritems():
        tmp_dict = {}
        this_v = v['version']
        if this_v.find("RB") == 0:
            this_m = this_v[3:this_v.find('2')-1]
        else:
            this_m = this_v[:this_v.find('2')-1]
        tmp_dict['version'] = this_v

        tmp_dict['endflag'] = v['endflag']
        tmp_dict['updated_at'] = v['updated_at']
        if ret.has_key(this_m.capitalize()):

            if tmp_dict['updated_at'] > ret[this_m.capitalize()].get('update_at'):
                ret[this_m.capitalize()] = tmp_dict
        else:
            ret[this_m.capitalize()] = tmp_dict

    return ret

def get_branch_svn_log(module, branch , start=None, end=None, limit = 5):

    job_svn_info = get_job_svn_info(module)


    if job_svn_info == False:
        return None

    if start == None or end == None:
        if branch == "trunk":
            cmd = 'svn log -l ' + str(limit) + ' ' + job_svn_info['trunk_url']

        else:
            cmd = 'svn log -l ' + str(limit) + ' ' + job_svn_info['branch_url'] + "/" + branch


    else:

        if branch == "trunk" :
            # trunk only support get last 10 records
            cmd = 'svn log -r '  + '{"' + start + '"}:'+ '{"' + end +'"} ' + job_svn_info['trunk_url']

        else:
            cmd = 'svn log -r '  + '{"' + start + '"}:'+ '{"' + end +'"} ' + job_svn_info['branch_url'] + "/" + branch


    status, output = commands.getstatusoutput(cmd)

    logger.debug("get_branch_svn_log cmd : " + cmd)
    if status !=0:
        return None
    else:
        records_list = output.split("------------------------------------------------------------------------");
        ret = []
        for i in records_list:
            if i == "":
                continue
            else:
                """
                r376258 | ligui | 2015-06-26 21:03:42 +0800 (五, 26  6 2015) | 1 line

                vote like
                """
                i = i.strip()
                tmp_l = i.split("\n")[0].split("|")
                tmp_l.append(i.split("\n")[-1])
                single_dict = {}
                single_dict['version'] = tmp_l[0].strip()
                single_dict['user'] = tmp_l[1].strip()
                single_dict['time'] = tmp_l[2].strip()
                single_dict['lines_cnt'] = tmp_l[3].strip()
                single_dict['comment'] = tmp_l[4].strip()

                ret.append(single_dict)
        return ret




class JenkinsTrigger(object):
    def __init__(self,
                 url,
                 data,
                 user_dict):
        """
        data : dict
        {"cmd":"ls",

        }
        """
        # 生成json串
        json_list = []
        if not data:
            print "no data provided"

        for k,v in data.iteritems():
            if k == "url":
                continue;
            tmp_dict = {}
            tmp_dict['name'] = k
            tmp_dict['value'] = v
            json_list.append(json.dumps(tmp_dict))

        # add user info
        for k,v in user_dict.iteritems():
            ud = {}
            ud['name'] = k
            ud['value'] = v
            json_list.append(json.dumps(ud))

        json_str = ",".join(json_list)

        # 组合curl cmd
        self.cmd = "curl -X POST " + url + " --user auto_test:auto_test" + " --form json='{\"parameter\": [" + json_str + "]}'"

    def trigger(self):
        #os.system(self.cmd)
        ret = subprocess.check_output(self.cmd, shell=True)
        if len(ret) > 0:
            logger.error("trigger fail: " + str(ret))
            return False
        else:
            return True

class JenkinsJobSwitch(object):
    def __init__(self, url, on_off):
        """
        on_off : 'disable', 'enable'
        """
        self.post_url = url + "/" + on_off
        self.cmd = "curl -X POST " + self.post_url + " --user auto_test:auto_test"

    def switch(self):
        ret = subprocess.check_output(self.cmd, shell=True);
        if len(ret) > 0:
            return False
        else:
            return True



class JenkinsInfo(object):

    def __init__(self, name, job=None, build=None):
        """
        :param name: jenkins job class, e.g. newlab , daily build
        :param job: jab name
        :return:
        """
        self.status = True
        self.jenkins_url = "http://jenkins.meiliworks.com/"
        self.name = name
        self.view_url = self.jenkins_url + "view/" + self.name + "/api/json?pretty=true"
        if job and build:
            self.job = job
            self.build = build
            # http://jenkins.meiliworks.com/view/newlab/job/newlabs_biz/14/api/json?pretty=true
            self.build_url = self.jenkins_url + "/job/" + self.job + "/" + self.build + "/api/json?pretty=true"

            r = requests.get(self.build_url)
            if r.status_code != 200:
                self.status = False
            self.ret =  r.json()

        elif job:
            self.job = job
            self.job_url = self.jenkins_url + "view/" + self.name + "/job/" + self.job + "/api/json?pretty=true"
            r = requests.get(self.job_url)
            if r.status_code != 200:
                self.status = False
                self.ret = {}
            else:
                self.ret = r.json()

        else:
            r = requests.get(self.view_url)
            if r.status_code != 200:
                self.status = False
            else:
                self.ret = r.json()['jobs']


    def get_ret(self):
        if self.status:
            return self.ret
        else:
            return {}

    def get_status(self):
        return self.status


def save_job_record(request, info=None):
    job = models.JobRecord()
    job.mail = request.session.get("django_name") if request.session.get("django_name") else request.GET.get("mail")
    if info == None:
        job.view_name = request.GET.get("view_name")
        job.job_name = request.GET.get("job_name")
        job.type = int(request.GET.get("type"))
        job.version = request.GET.get("version")
    else:
        job.view_name = info.get("view_name")
        job.job_name = info.get("job_name")
        job.type = int(info.get("type"))
        job.version = info.get("version")
    job.save()


def get_job_record_by_type_job_name(job_name, type , limit = 5):
    ret = []
    if job_name == "newlabs_biz" or job_name =="newlabs_shanghaife":

        ret_q = models.JobRecord.objects.filter(type=type,job_name__startswith=job_name).order_by('-ctime')[:int(limit)]    # sealed info only
    else:
        ret_q = models.JobRecord.objects.filter(type=type,job_name=job_name).order_by('-ctime')[:int(limit)]    # sealed info only

    for i in ret_q:
        data = {}
        data['comment'] = u"封板"
        data['version'] = i.version
        data['user'] = i.mail
        data['time'] = public.datetime2str(i.ctime)
        ret.append(data)
    return ret



def get_latest_job_record(job_name, specified=False):
    # get jobinfo
    # specified 参数 True说明就是要看biz或shanghaife某个模块的

    data = {}

    if (job_name.startswith("newlabs_biz") or job_name.startswith("newlabs_shanghaife") ) and specified==False:


        if job_name.startswith("newlabs_biz"):
            startwith = "newlabs_biz"
        elif job_name.startswith("newlabs_shanghaife"):
            # consider job_name == newlabs_shanghaife (not like newlabs_shanghaife_common),
            # so use newlabs_shanghaif for startwith param
            startwith = "newlabs_shanghaife"


        if len(models.JobRecord.objects.filter(type=3,job_name__startswith=startwith)) != 0:
            ret = models.JobRecord.objects.filter(type=3,job_name__startswith=startwith).latest('ctime')
            data['sealed_version'] = ret.version
        else:
            data['sealed_version'] = "unknown"


        if len(models.JobRecord.objects.filter(type=2,job_name__startswith=startwith)) != 0:
            ret = models.JobRecord.objects.filter(type=2,job_name__startswith=startwith).latest('ctime')
            data['newlab_version'] = ret.version
            data['user'] = ret.mail
        else:
            data['newlab_version'] = 'unknown'
            data['user'] = 'unknown'

    else:

        if len(models.JobRecord.objects.filter(job_name=job_name, type=3)) != 0:
            ret = models.JobRecord.objects.filter(job_name=job_name, type=3).latest('ctime')
            data['sealed_version'] = ret.version
        else:
            data['sealed_version'] = "unknown"


        if len(models.JobRecord.objects.filter(job_name=job_name, type=2)) != 0:
            ret = models.JobRecord.objects.filter(job_name=job_name, type=2).latest('ctime')
            data['newlab_version'] = ret.version
            data['user'] = ret.mail
        else:
            data['newlab_version'] = 'unknown'
            data['user'] = 'unknown'
    if data.get("user"):
        tmp = web_utils.get_user_dict(data.get("user"))
        if tmp:
            data["user"] = tmp.get("name", "")
    return data


def get_all_bizshanghaife_jobname(biz_or_shanghife):
    startwith = "newlabs_" + biz_or_shanghife
    ret =  models.JobRecord.objects.filter(type=3,job_name__startswith=startwith).distinct('job_name')
    return models.JobRecord.objects.filter(type=3,job_name__startswith=startwith)


def get_seal_or_newlab_version(module = None):
    if module:
        if module != "shanghaife" and module != "biz":
            job_name = "newlabs_" + module.lower()
            ret = get_latest_job_record(job_name, True)
            if ret.get("sealed_version"):
                return {module:ret.get("sealed_version")}
            else:
                return {module:ret.get("newlab_version")}
        else:
            # get all biz fe job records
            # return all module
            ret_dict = {}

            for i in models.JobRecord.objects.values('job_name').distinct():
                if module == 'biz':
                    if 'biz' in i['job_name'] :
                        this_ret = get_latest_job_record(i['job_name'], True)
                    else:
                        continue
                elif module == "shanghaife":
                    if 'shanghaife' in i['job_name'] :
                        this_ret = get_latest_job_record(i['job_name'], True)
                    else:
                        continue

                if this_ret.get('sealed_version'):
                    ret_dict[i['job_name'].replace("newlabs_","")] = this_ret.get('sealed_version')
                else:
                    ret_dict[i['job_name'].replace("newlabs_","")] = this_ret.get('newlab_version')
            return ret_dict

    else:
        # return all module
        ret_dict = {}
        for i in models.JobRecord.objects.values('job_name').distinct():
            this_ret = get_latest_job_record(i['job_name'], True)
            if this_ret.get('sealed_version'):
                ret_dict[i['job_name'].replace("newlabs_","")] = this_ret.get('sealed_version')
            else:
                ret_dict[i['job_name'].replace("newlabs_","")] = this_ret.get('newlab_version')
        return ret_dict



def diff_branch(module ,b1, b2):
    try:
        job = models.JobInfo.objects.get(name = 'newlabs_' + module)
    except:
        return False
    svn_path = job.branch
    p1 = svn_path + '/' + b1
    p2 = svn_path + '/' + b2
    cmd = "svn diff --old " + p1 + " --new " + p2
    log_file = "/tmp/" + b1 + "_diff_" + b2 + ".log"
    same_file = "/tmp/" + b2 + "_diff_" + b1 + ".log"


    if (not os.path.exists(log_file)) and (not os.path.exists(same_file)):
        try:
            ret = subprocess.check_output(cmd, shell=True)
        except:
            return False
        fp = open(log_file,"w+b")
        fp.write(ret)
        fp.close()
        return ret
    else:
        if os.path.exists(log_file):
            fp = open(log_file)

        else:
            fp = open(same_file)
        ret = fp.read()
        fp.close()
        return ret



def get_online_status(day=None):
    """
    :author: yechengzhou
    :param day: 希望得到哪天的信息
    :return: json
    """

    if day==None:  # 无参数取今天
        day = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 获取上线信息, 实时
    userMainUrl = "http://syspush.meilishuo.com/opssys/index.php/Marklog/getLook";
    req = urllib2.Request(userMainUrl)
    resp = urllib2.urlopen(req).read()
    if len(resp) == 0 or type(eval(resp)) == type([]):
        return False #上线信息不存在

    online_dict = eval(resp)
    ret_dict = {}
    for k,v in online_dict.iteritems():
        tmp_dict = {}
        this_v = v['version']
        if this_v.find("RB") == 0:
            this_m = this_v[3:this_v.find('2')-1]
        else:
            this_m = this_v[:this_v.find('2')-1]
        tmp_dict['version'] = this_v
        tmp_dict['project'] = k
        tmp_dict['endflag'] = v['endflag']
        tmp_dict['updated_at'] = v['updated_at']
        if this_m.lower() in ret_dict:
            ret_dict[this_m.lower()] = []
            ret_dict[this_m.lower()].append(tmp_dict)
        else:
            ret_dict[this_m.lower()] = []
            ret_dict[this_m.lower()].append(tmp_dict)


    return ret_dict



def get_job_svn_info(module):

    try:
        job = models.JobInfo.objects.get(name = 'newlabs_' + module)
    except:
        return False

    ret = {}
    ret['branch_url'] = job.branch
    ret['trunk_url'] = job.trunk

    return ret



def get_build_specific_info(builds_url):
    if type(builds_url) == type([]):
        ret_list = []
        for url in builds_url:
            query_url = url + "api/json/?pretty=True"
            r = requests.get(query_url)
            if r.status_code != 200:
                return False
            ret_list.append(r.json())
        return ret_list
    else:
        query_url = builds_url + "api/json/?pretty=True"
        r = requests.get(query_url)
        if r.status_code != 200:
            return False
        return r.json()


def get_latest_online_version(content , jobname):
    # get tag name from JobInfo
    jobinfo = models.JobInfo.objects.filter(name=jobname)
    if not jobinfo:
        return False
    tag = jobinfo[0].tag
    # request sys api
    online_info = content.get(tag)
    if online_info:
        return online_info
    else:
        return False

def trigger_online_package():
    data = public.get_data("http://syspush.meilishuo.com/opssys/index.php/Marklog/getLastVersion")
    if data:
        d = data.strip().split("\n\n")
        for i in d:
            try:
                t = i.strip().split(" ")
                if len(t) == 2:
                    online, created = models.OnlinePackage.objects.get_or_create(name=t[0])
                    online.package = t[1]
                    online.save()
            except:
                pass

def get_online_package():
    online = public.model_to_list(models.OnlinePackage.objects.all())
    ret = {}
    for d in online:
        ret[d.get("name")] = d.get("package")
    return ret

# 2015 9 2
def get_version_ctime(version):
    info = models.JobRecord.objects.filter(version=version, type=3)
    if len(info) != 0:
        time = info[0].ctime
        return time
    else:
        return False

def get_latest_job_record_list():
    job_record = models.JobRecord.objects.all().order_by("-id")[0:5]
    ret = []
    for job in job_record:
        tmp = model_to_dict(job)
        tmp["user"] = tmp.get("mail", "").replace("@meilishuo.com", "")
        tmp["job_name"] = tmp.get("job_name", "").replace("newlabs_", "")
        tmp["ctime"] = public.datetime2str(job.ctime)
        ret.append(tmp)
    return ret

def get_public(request):
    ret = {}
    ret["group_id"] = request.GET.get("group_id")
    ret["auth"] = web_utils.check_auth(public.get_user_mail(request), public.WORK_PRE_LAUNCH)
    ret["group"] = get_group()
    if ret["group_id"]:
        ret["group_id"] = int(ret["group_id"])
    elif ret["group"]:
        ret["group_id"] = -1
    else:
        ret["group_id"] = 0
    return ret

def get_group(id=None):
    return public.get_model(models.Group, id)

def save_group(data):
    m = models.Group(**data)
    m.save()
    return m.id

def rm_group(group_id):
    group = models.GroupJob.objects.filter(group_id=group_id)
    if len(group) > 0:
        return u"分组中包含job，请先去掉！"
    models.Group.objects.filter(id=group_id).delete()
    return True

def get_job_info(id=None):
    return public.get_model(models.JobInfo, id)

def get_job_by_name(name):
    jobs = models.JobInfo.objects.filter(name=name)
    if len(jobs) == 0:
        return False
    else:
        return public.model_to_dict(jobs[0])

def get_group_by_job(job_id):
    items = models.GroupJob.objects.filter(job_id=job_id)
    if len(items) == 0:
        return False
    else:
        return public.model_to_list(items)


def get_job_html(group_id):
    group_job = models.GroupJob.objects.filter(group_id=group_id)
    id_list = []
    for d in group_job:
        id_list.append(d.job_id)
    job_list = get_job_info()
    body = ""
    for d in job_list:
        body += "<tr>"
        body += '<td>%s</td>' % d["name"]
        body += '<td>%s</td>' % d["tag"]
        if d["id"] in id_list:
            body += '<td><input type="checkbox" name="cklist" value="%s" checked="checked"></td>' % d["id"]
        else:
            body += '<td><input type="checkbox" name="cklist" value="%s"></td>' % d["id"]
        body += "<tr>"

    ret = u'''<input type="hidden" id="group_id" value="%s"><table class="table table-striped table-bordered table-hover table-condensed">
        <thead>
        <tr>
          <th>名称</th>
          <th>标签</th>
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
        ''' % (group_id, body)
    return ret

def bind_job(data):
    group_id = data.get("group_id")
    job_list = data.get("job_list")
    tag = data.get("tag")
    if str(tag) == "1":
        for job_id in job_list:
            models.GroupJob.objects.filter(group_id=group_id, job_id=job_id).delete()
    else:
        for job_id in job_list:
            models.GroupJob.objects.get_or_create(group_id=group_id, job_id=job_id)
    return True

def get_group_jobs(group_id):
    group_job = models.GroupJob.objects.filter(group_id=group_id)
    ret = []
    for d in group_job:
        job = model_to_dict(models.JobInfo.objects.get(id=d.job_id))
        #添加job对应的状态, 封板版本，当前版本，操作者等相关信息
        ret.append(job)
    return ret

def get_jobs_not_group():
    jobs_have_group = set()
    for i in models.GroupJob.objects.all():
        jobs_have_group.add(i.job_id)

    all_jobs = models.JobInfo.objects.all()
    ret = []
    for i in all_jobs:
        if i.id in jobs_have_group:
            continue
        else:
            ret.append(public.model_to_dict(i))
    return ret

def get_collection(request):
    user = public.get_user_mail(request)
    collect = models.Collection.objects.filter(user=user)
    job_list = []
    for d in collect:
        job_list.append(d.job_id)
    return public.model_to_list(models.JobInfo.objects.filter(id__in=job_list))

def save_collection(request):
    user = public.get_user_mail(request)
    data = json.loads(request.body)
    job_id = data.get("job_id")
    tag = data.get("tag")
    if user and job_id:
        #取消收藏
        if str(tag) == "1":
            models.Collection.objects.filter(user=user, job_id=job_id).delete()
        else:
            models.Collection.objects.get_or_create(user=user, job_id=job_id)
        return True
    else:
        return u"用户登录失效，请刷新页面！"


