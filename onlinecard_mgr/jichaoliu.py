# coding:utf8

import public
import json
import utils
import urllib
import urllib2
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def get_cards_info(request):
    url="http://sys-request.meilishuo.com/workflow/index.php/Index/listWaitJson"
    req = urllib2.urlopen(url).read()
    retData=utils.getProduct_cards(req);
    return JsonResponse(retData)

def save_push_status(request):
    try:
        url="http://syspush.meilishuo.com/opssys/index.php/Marklog/getLook"
        req = urllib2.urlopen(url).read()
    except Exception, e:
        ret={}
        ret["code"]="-1"
        ret["message"]="op 接口超时"
        return JsonResponse(ret)
    retData=utils.save_push_status(req);
    return JsonResponse(retData)

def get_push_status(request):
    data = {}
    if request.method == "GET":
        data["time"] = request.GET.get("time")
        data["area"] = request.GET.get("location")
        data["module"]=request.GET.get("version")
        rtData=utils.get_push_status(data)
    else:
        return public.fail_result_http(u"该接口只支持GET数据")

    return JsonResponse(rtData)

@csrf_exempt
@public.auth_user
def showList(request):
    group=request.GET.get("group")
    page=request.GET.get("page")
    data=utils.get_group_name(request)
    url=public.JAVA_HOST + "/onlinecard/api/online_cards?group="+group+"&pageNum="+page
    req = public.get_data(url)
    req_dict = json.loads(req)
    return render(request,'onlinecards_list.html',{"data":data,"group":req_dict,"group_id":long(group),"pageNum":long(page)})


@csrf_exempt
@public.auth_user
def deadlist(request):
    '''
    死链列表
    :param request:
    :return:
    '''
    ret = {}
    page=request.GET.get("page")
    url=public.JAVA_HOST + "/deadlink/api/results?page="+page
    req = public.get_data(url)
    compressedData = json.loads(req)
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1
    if compressedData:
        if compressedData["size"]%10 >0:
            ret['last_page']=compressedData["size"]/10+1
        else:
            ret['last_page']=compressedData["size"]/10
    else:
        ret['last_page']=0

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
    ret['pre'] = page - 1
    if page == ret['last_page']:
        ret['next'] = -1
    else:
        ret['next'] = page + 1

    return render(request,'deadList.html',{"data":compressedData['data'],"ret":ret})


@csrf_exempt
@public.auth_user
def deadDetail(request):
    '''
    死链详情
    :param request:
    :return:
    '''
    id=request.GET.get("id")
    url=public.JAVA_HOST + "/deadlink/api/details?id="+id
    req = public.get_data(url)
    retdata=json.loads(req)

    return render(request,'deadDetail.html',{"data":retdata})

@csrf_exempt
@public.auth_user
def getOnline(request):
    '''
    点击上线
    :param request:
    :return:
    '''
    area=request.POST.get("area")
    data=request.POST.get("data")
    f=open('online.log','w')
    print >>f,'area=>',area
    print >>f,'data=>',data

    # url=public.JAVA_HOST + "/deadlink/api/details?area="+area
    # req = public.get_data(url)
    # retdata=json.loads(req)
    retdata={}
    retdata["code"]=0
    retdata["mes"]="true"

    return JsonResponse(retdata)