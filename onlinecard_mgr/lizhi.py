# coding:utf8

from django.shortcuts import render, redirect
from data_mgr import utils as data_utils
import public
import requests
import json
#import pdb; pdb.set_trace()

@public.auth_user
def card_detail(request):
    online_card_id = request.GET.get('card_id')

    try:
        card_info = requests.get(public.JAVA_HOST + '/onlinecard/api/online_card?id=' + online_card_id).json()
    except:
        card_info = {}

    if card_info.get('product_card'):
        for i in card_info.get('product_card'):
            if i.get('need_qa'):
                if not card_info.has_key('need_qa'):
                    card_info['need_qa'] = []
                card_info['need_qa'].append(i)
            else:
                if not card_info.has_key('not_need_qa'):
                    card_info['not_need_qa'] = []
                card_info['not_need_qa'].append(i)

    public_date = data_utils.get_public(request)
    card_info["public"] = public_date
    email=card_info.get('notification_email').split(',')
    card_info['notification_email']=email
    return render(request, "onlinecard_detail.html", {'data': card_info})

"""
邮件接口
"""
def showMail(request):
    online_card_id = request.GET.get('card_id')
    try:
        card_info = requests.get(public.JAVA_HOST + '/onlinecard/api/online_card?id=' + online_card_id).json()
    except:
        card_info = {}

    if card_info.get('product_card'):
        for i in card_info.get('product_card'):
            if i.get('need_qa'):
                if not card_info.has_key('need_qa'):
                    card_info['need_qa'] = []
                card_info['need_qa'].append(i)
            else:
                if not card_info.has_key('not_need_qa'):
                    card_info['not_need_qa'] = []
                card_info['not_need_qa'].append(i)
    email=card_info.get('notification_email').split(',')
    print "email=",email
    emailStr=''
    j=1
    for a in email:
        emailStr=emailStr+a+", "
        print "emailStr=",emailStr
        if (j % 3)==0:
            emailStr=emailStr+"<br/>"
        j=j+1
    card_info['notification_email']=email
    return render(request, "onlinecard_forMail.html", {'data': card_info})