# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''


import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^check_alive', views.check_alive),
    url(r'^redirect_login', views.redirect_login),
    url(r'^$', views.home),
    url(r'^performance$', views.performance_view),
    url(r'^performance/detail', views.performance_detail_view),
    url(r'^mob$', views.mob_view),
    url(r'^mob/detail', views.mob_detail_view),
    url(r'^get/interface', views.get_interface_view),
    url(r'^promotion', views.get_promotion_record_view),
    url(r'^svn/test', views.get_svn_history_view),
    url(r'^user/logout', views.user_logout_view),
    url(r'^jenkins',views.jenkins_view),

    url(r'^svn/history', views.get_svn_test_view),
    url(r'^save/release', views.save_Release_Plan),
    url(r'^save/package', views.save_package_status),
    url(r'^save/back_information', views.save_goback_information),
    url(r'^save/information', views.save_information),

    url(r'^cl', views.svn_history_only),
    url(r'^timeline', views.timeline),
    url(r'^online$', views.online_info),

    url(r'^ci/dashboard', views.dashboard_view),
    url(r'^ci/task', views.get_task_list_view),
    url(r'^ci/subtask', views.sub_task_view),
    url(r'^ci/jobs', views.jobs_view),
    url(r'^ci/module', views.module_config_view),
    url(r'^ci/job/create', views.job_create_view),
    url(r'^ci/job/modify', views.job_modify_view),
    url(r'^ci/job/seq', views.job_seq_view),
    url(r'^ci/job/bind', views.job_bind_view),

    url(r'^job/show', views.job_job_show_view),
    url(r'^job/config', views.job_job_config_view),
    url(r'^job/seq_conf', views.job_seq_config_view),
    url(r'^job/hex',views.job_hex_view),


    url(r'^get/user',views.get_user_view),
    url(r'^set/auth',views.set_auth_view),

    # test
    url(r'^prelaunch', views.pre_launch),
    url(r'^sheet', views.sheet),

    url(r'get_pre_launch_info', views.get_pre_launch_info),

    url(r'get_seal_version',views.get_seal_version),

    #url(r'task_status',views.hehe),

    url(r'^sh',views.sheet_version),
    url(r'small_log', views.sheet_small_module_log),
    url(r'^spreview', views.sheet_preview),

    url(r'sheet', views.sheet_version),

)
