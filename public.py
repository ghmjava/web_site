# coding:utf-8
import datetime
import time
import traceback
import json
import functools
import urllib
import urllib2,cookielib
import requests
import math

from django.http import HttpResponse
from django.shortcuts import redirect
from django.forms.models import model_to_dict




JAVA_HOST = "http://agile.meiliworks.com"
#test
#AUTH_ROOT_URL = "http://apitest.speed.meilishuo.com"
#APP_KEY = "100001"
#APP_SECRET = "543774710dcc91a7e52428bf02ac8c41"

#online
AUTH_ROOT_URL = "http://api.speed.meilishuo.com"
APP_KEY = "100055"
APP_SECRET = "60f543fe273eb6e7a137b5041741491a"

WEB_URL = "http://agile.meiliworks.com/"
#WEB_URL = "http://192.168.164.175:8000/"
AUTH_URL = "%s/oauth/authorize?client_id=%s&response_type=code&redirect_uri=" % (AUTH_ROOT_URL, APP_KEY)
REDIRECT_URL = "/redirect_login?redirect_login="

JENKINS_URL = "http://jenkins.meiliworks.com"
JOB_PARAM = "NEXT_JOB_PARAM"   #传递参数格式为: NEXT_JOB_PARAM=key::value&&key1::value1

JENKINS_USER = "auto_test"
JENKINS_PASSWORD = "auto_test"

SUPER_FLAG = "super"
#每页显示记录条数
PAGING_NUM = 10
#显示最大分页数
MAX_PAGING = 11

JENKINS_COLOR_FAIL = "red"
JENKINS_COLOR_PASS = "blue"
JENKINS_COLOR_DISABLED = "disabled"
JENKINS_COLOR_NOT_BUILD = "notbuilt"
JENKINS_COLOR_RUN = "anime"

#jenkins job 状态标识
JENKINS_UNKNOWN = 0
JENKINS_PASS = 1
JENKINS_FAIL = 2
JENKINS_DISABLED = 3
JENKINS_NOT_BUILD = 4
JENKINS_RUN = 5

# 数据分页条数
PAGE_NUM = 20
PERCENT = 0.2

# 状态码
STATUS_UNKNOWN = -1
STATUS_CREATE = 0
STATUS_WAIT = 1
STATUS_RUNNING = 2
STATUS_PASS = 3
STATUS_FAIL = 4
STATUS_MANUAL_PASS = 5

#运行类型
RUN_TYPE_DEBUG = 0
RUN_TYPE_MANUAL = 1
RUN_TYPE_AUTO = 2
RUN_TYPE_TIMER = 3

LOWER_STATUS_FAIL = "fail"
LOWER_STATUS_SUCCESS = "success"

ENV_MOB = "MOB"
ENV_NEWLAB = "NEWLAB"

TYPE_CPU = "CPU"
TYPE_MEMORY = "MEMORY"
TYPE_POWER = "POWER"
TYPE_TRAFFIC = "TRAFFIC"
TYPE_TIME = "TIME"
TYPE_LIST = (TYPE_CPU, TYPE_MEMORY, TYPE_POWER, TYPE_TRAFFIC, TYPE_TIME)
TYPE_DICT = {TYPE_CPU: u'CPU', TYPE_MEMORY: u"内存", TYPE_POWER: u"CPU耗电", TYPE_TRAFFIC: u"流量", TYPE_TIME: u"安装和启动时间"}

SCENE_MONKEY = "MONKEY"
SCENE_AUTO = "AUTO"
SCENE_SLEEP = "SLEEP"
SCENE_LIST = (SCENE_MONKEY, SCENE_AUTO, SCENE_SLEEP)

INTERFACE_TYPE_HOT = "HOT"
INTERFACE_TYPE_WEB = "WEB"

#预上线
WORK_PRE_LAUNCH = 1
#复合监控
WORK_MONITOR = 2
#持续集成
WORK_CI = 3
#性能评估
WORK_ASSESS = 4

'''
function log black menu
'''
FUNC_BLACK_MENU = []

#######################################################################################

def post_data(url, data):
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()

def get_data(url):
    return urllib2.urlopen(url).read()

def get_url(request):
    host = request.META.get("HTTP_HOST")
    path = request.META.get("PATH_INFO")
    query = str(request.META.get("QUERY_STRING"))
    query=urllib.quote(query)
    query=urllib.quote(query)
    query=urllib.quote(query)
    if host:
        url = "http://" + host
        if path:
            url += path
        if query:
            url += "?" + query
    else:
        url = WEB_URL
    return url

def auth_user(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        request = args[0]
        name = request.session.get("django_name")
        code = request.GET.get("code")
        if name or code:
            result = func(*args, **kwargs)
            return result
        else:
            host = request.META.get("HTTP_HOST")
            url = "http://" + host
            url += REDIRECT_URL + get_url(request)
            return redirect(AUTH_URL+url)

    return decorator

def get_user_mail(request):
    return request.session.get("django_mail") if request.session.get("django_mail") else ""

def datetime2str(dt, _format=r'%Y-%m-%d %H:%M:%S'):
    if dt:
        result = dt.strftime(_format)
    else:
        result = ""
    return result


def str2datetime(time_str, _format=r'%Y-%m-%d %H:%M:%S'):
    if time_str:
        result = datetime.datetime.strptime(time_str, _format)
    else:
        result = None
    return result

def time2datetime(number, _format=r'%Y-%m-%d %H:%M:%S'):
    number = float(number)
    result = time.strftime(_format, time.localtime(number))
    return result

def success_result_http(data=None):
    result = Result(LOWER_STATUS_SUCCESS,
                    "",
                    data)
    return result.http()

def fail_result_http(message="", data=None):
    """

    :rtype : object
    """
    result = Result(LOWER_STATUS_FAIL,
                    message,
                    data)
    return result.http()

def exception_result_http():
    result = Result()
    return result.exception_http()

def access_logger(func):
    #logging
    func()
    return func

class Result(object):
    def __init__(self,
                 status=LOWER_STATUS_SUCCESS,
                 message="",
                 data=None):
        self.result = {"status":status,
                       "message":message,
                       "data":data}

    def set_success(self):
        self.result["status"] = LOWER_STATUS_SUCCESS

    def set_fail(self):
        self.result["status"] = LOWER_STATUS_FAIL

    def set_message(self, message):
        self.result["message"] = message

    def set_data(self, data):
        self.result["data"] = data

    def json(self):
        return self.result

    def http(self, code=200):
        result = self._dumps()
        return HttpResponse(result, "application/json", code)

    def exception_http(self):
        self.set_fail()
        self.set_message(traceback.format_exc())
        self.set_data(None)
        return self.http(500)

    def exception_json(self):
        self.set_fail()
        self.set_message(traceback.format_exc())
        self.set_data(None)
        return self.json()

    def _dumps(self):
        return json.dumps(self.result)

def paging_algorithm(total, page_current, page_num=PAGING_NUM):
    '''
    :param total: 记录总条数
    :param current: 当前页码
    :return:
    '''
    ret = {}
    if total > page_num:
        page_current = int(page_current)
        ret["total"] = total
        ret["page"] = {}
        start = (page_current-1) * page_num
        end = page_current * page_num if page_current * page_num < total else total
        page_total = int(math.ceil(total * 1.0 / page_num))
        page_start = 1
        page_end = page_total + 1
        if page_total > MAX_PAGING:
            half = MAX_PAGING/2
            if page_current + half > page_end:
                page_start = page_end - 2 * half
            if page_current - half < page_start:
                page_end = page_start + 2 * half
            if page_current + half <= page_end and page_current - half >= page_start:
                page_start = page_current - half
                page_end = page_current + half + 1

        if page_current == 1:
            flag = "start"
        elif page_current == page_total:
            flag = "end"
        else:
            flag = "other"
        ret["start"] = start
        ret["end"] = end
        ret["flag"] = flag
        ret["page"]["current"] = page_current
        ret["page"]["total"] = page_total
        ret["page"]["start"] = page_start
        ret["page"]["end"] = page_end
        ret["page"]["list"] = range(page_start, page_end)
    return ret

def model_to_list(instance, fields=None, exclude=None):
    ret =[]
    for m in instance:
        ret.append(model_to_dict(m, fields, exclude))
    return ret

def get_model(instance, id=None, fields=None, exclude=None):
    if id:
        module = instance.objects.get(id=id)
        return model_to_dict(module, fields, exclude)
    else:
        module = instance.objects.all()
        return model_to_list(module, fields, exclude)
