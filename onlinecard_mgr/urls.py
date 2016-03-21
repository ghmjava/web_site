# coding:utf8
'''
Created on 2015-12-02

@author: xuemengwang
'''

from django.conf.urls import patterns, url
import jichaoliu
import lizhi

urlpatterns = patterns('',

    url(r'^online_card/get_cards', jichaoliu.get_cards_info),
    url(r'^online_card/cards_status', jichaoliu.save_push_status),
    url(r'^online_card/getStatus', jichaoliu.get_push_status),
    url(r'^online_card/showlist', jichaoliu.showList),
    url(r'^online_card/getOnline', jichaoliu.getOnline),
    url(r'^online_card/showmail', lizhi.showMail),
    url(r'^online_card/card_detail', lizhi.card_detail),



    url(r'^deadlink/list', jichaoliu.deadlist),
    url(r'^deadlink/detail',jichaoliu.deadDetail),
)


