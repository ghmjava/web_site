# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

import json
import logging
import traceback
from django.db.models import Q
from django.forms.models import model_to_dict

import public
import models

def set_user_cookie(request):
    try:
        code = request.GET.get("code")
        if code:
            access_token_url = "%s/oauth/access_token" % public.AUTH_ROOT_URL
            statuses_url = "%s/oauth/statuses" % public.AUTH_ROOT_URL
            data = {}
            data["client_id"] = public.APP_KEY
            data["client_secret"] = public.APP_SECRET
            data["grant_type"] = "authorization_code"
            data["redirect_uri"] = public.WEB_URL
            data["code"] = code
            ret = json.loads(public.post_data(access_token_url, data))
            data = {}
            data["client_id"] = public.APP_KEY
            data["access_token"] = ret["access_token"]
            ret = json.loads(public.post_data(statuses_url, data))
            d = ret["data"]
            name = d["name"]
            mail = d["mail"]
            depart = d["depart"]
            request.session["django_name"] = name
            request.session["django_mail"] = mail
            request.session["django_depart"] = depart
            user, created = models.UserInfo.objects.get_or_create(mail=mail)
            if not created:
                user.times += 1
            else:
                user.times = 1
            user.name = name
            user.depart = depart
            user.options = json.dumps(d)
            user.save()
    except:
        logging.error(traceback.format_exc())

def get_user_cookie(request):
    data = {}
    try:
        data["name"] = request.session["django_name"]
        data["mail"] = request.session["django_mail"]
        data["depart"] = request.session["django_depart"]
    except:
        pass
    return data

def del_user_cookie(request):
    del request.session["django_name"]
    del request.session["django_mail"]
    del request.session["django_depart"]

def get_user_dict(mail):
    ret = {}
    if not id:
        return ret
    user = models.UserInfo.objects.filter(mail=mail)
    if user:
        ret = model_to_dict(user[0])
    return ret

def get_user_info(data):
    work_id = data.get("work_id")
    flag = data.get("flag")
    q = data.get("q")
    ret = {}
    if not work_id:
        return ret
    if q:
        qset = Q(mail__icontains=q) | Q(name__icontains=q) | Q(depart__icontains=q)
        user = models.UserInfo.objects.filter(qset)
    else:
        user = models.UserInfo.objects.all()
    if work_id:
        work_id = int(work_id)
    user_list = []
    admin_list = []
    for u in user:
        tmp = model_to_dict(u)
        del tmp["options"]
        auth, created = models.Authorization.objects.get_or_create(user_id=u.id, work_id=work_id)
        tmp["admin"] = auth.admin
        tmp["write"] = auth.write
        if flag == public.SUPER_FLAG:
            if tmp["auth"]:
                admin_list.append(tmp)
            elif tmp["admin"]:
                user_list.insert(0, tmp)
            else:
                user_list.append(tmp)
        else:
            if tmp["admin"]:
                admin_list.append(tmp)
            elif tmp["write"]:
                user_list.insert(0, tmp)
            else:
                user_list.append(tmp)
    if admin_list:
        user_list = admin_list + user_list

    page_current = data.get("page_current", 1)
    if not page_current:
        page_current = 1
    else:
        page_current = int(page_current)
    page = public.paging_algorithm(len(user_list), page_current, 50)
    ret["page"] = page
    ret["user_list"] = user_list
    if page:
        ret["user_list"] = user_list[page["start"]:page["end"]]
    return ret

def set_auth(request):
    mail = request.session.get("django_mail")
    data = json.loads(request.body)
    flag = data.get("flag")
    work_id = int(data.get("work_id")) if data.get("work_id") else 0
    set_type = data.get("set_type")
    id_list = data.get("id_list")
    if not (work_id and mail):
        return u"用户未登录或者参数有误！"
    user = models.UserInfo.objects.get(mail=mail)
    super = user.auth
    auth = models.Authorization.objects.filter(user_id=user.id, work_id=work_id)
    admin = 0
    if auth:
        admin = auth[0].admin
    if flag == public.SUPER_FLAG:
        if not super:
            return u"非超级用户不能设置管理员！"
        if set_type == "set":
            models.Authorization.objects.filter(user_id__in=id_list, work_id=work_id).update(admin=1)
        else:
            models.Authorization.objects.filter(user_id__in=id_list, work_id=work_id).update(admin=0)
    else:
        if not (admin or super):
            return u"非管理员不能够设置可写权限！"
        if set_type == "set":
            models.Authorization.objects.filter(user_id__in=id_list, work_id=work_id).update(write=1)
        else:
            models.Authorization.objects.filter(user_id__in=id_list, work_id=work_id).update(write=0)
    return None

def check_auth(mail, work_id):
    user = models.UserInfo.objects.get(mail=mail)
    ret = {}
    ret["user_id"] = user.id
    ret["work_id"] = work_id
    ret["auth"] = user.auth
    ret["admin"] = 0
    ret["write"] = 0
    if work_id:
        work_id = int(work_id)
        auth, created = models.Authorization.objects.get_or_create(user_id=user.id, work_id=work_id)
        ret["admin"] = auth.admin
        ret["write"] = auth.write
    if ret["auth"] or ret["admin"]:
        ret["write"] = 1
    if ret["auth"]:
        ret["admin"] = 1
    return ret

