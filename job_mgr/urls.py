# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''


import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^save/job', views.save_job_view),
    url(r'^get/job$', views.get_job_view),
    url(r'^get/job_all', views.get_job_all_view),
    url(r'^set/next_job', views.set_next_job_view),
    url(r'^rm/job', views.rm_job_view),
    url(r'^get/pre_list', views.get_pre_list_view),
    url(r'^static/job', views.static_job_view),
    url(r'^auto/check_job_status', views.auto_check_job_status_view),
)
