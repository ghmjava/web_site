# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''


import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'^save/module$', views.save_module_view),
    url(r'^get/module$', views.get_module_view),
    url(r'^get/module/list', views.get_module_list_view),

    url(r'^save/task', views.save_task_view),
    url(r'^get/task$', views.get_task_view),
    url(r'^get/task/list', views.get_task_list_view),
    url(r'^start/task', views.start_task_view),
    url(r'^get/task_status', views.get_task_status_view),
    url(r'^merge/task_record', views.merge_task_record_view),
    url(r'^rm/task', views.rm_task_view),
    url(r'^manual/task_config', views.manual_task_config_view),

    url(r'^save/sub_task', views.save_sub_task_view),
    url(r'^set/sub_task_order', views.set_sub_task_order_view),
    url(r'^get/sub_task$', views.get_sub_task_view),
    url(r'^get/sub_task_info', views.get_sub_task_info_view),
    url(r'^rm/sub_task', views.rm_sub_task_view),

    url(r'^bind/sub_task_job', views.bin_sub_task_job_view),
    url(r'^set/sub_task_job_order', views.set_sub_task_job_order_view),
    url(r'^get/sub_task_job', views.get_sub_task_job_list_view),
    url(r'^rm/job', views.rm_job_view),
    url(r'^save/job_reason', views.save_job_reason_view),

    url(r'^save/module_job', views.save_module_job_view),
    url(r'^get/module_job$', views.get_module_job_view),
    url(r'^get/module_job_list', views.get_module_job_list_view),

    url(r'^static/dashboard', views.static_dashboard_view),

    url(r'^build/job', views.build_job),
    url(r'^disable/job', views.disable_job),
    url(r'^enable/job', views.enable_job),
    url(r'^report/result', views.report_result),

    url(r'^get/fail_type', views.get_fail_type_view),
)
