# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''


import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^save/dashboard', views.save_dashboard_view),
    url(r'^save/promotion/record', views.save_promotion_record_view),
    url(r'^get/dashboard$', views.get_dashboard_view),
    url(r'^get/dashboard/info', views.get_dashboard_view),
    url(r'^static/dashboard', views.static_dashboard_view),
    url(r'^get/interface', views.get_interface_info_view),
    url(r'^get/promotion/record', views.get_promotion_record_view),
    url(r'^save/svn', views.save_svn_history_view),
    url(r'^get/svn', views.get_svn_history_view),
    url(r'^save/report', views.save_auto_report),
    url(r'^get/sealed/info', views.get_sealed_info), # 封板信息与newlab的diff
    url(r'^save/sealed/info', views.save_sealed_info),
    url(r'^get/sealonline', views.get_sealdiffonline), # 封板信息与online的diff
    url(r'^get/branchsvnlog', views.get_branch_svn_log), # 获取branch 的svn log
    url(r'^trigger/jenkins',views.jenkins_trigger), # 触发jenkinsjob 支持参数
    url(r'^get/jenkins_info', views.jenkins_info),
    url(r'^get/jenkins_builds_info', views.jenkins_builds_info),
    url(r'^switch/jenkins',views.jenkins_switch),
    url(r'^save/job/record',views.save_job_record_view),
    url(r'^get/build/status',views.get_build_status),
    url(r'^get/sealedversion',views.get_sealed_or_newlab_version),
    url(r'^get/branch/diff',views.get_branch_diff),
    url(r'^get/history',views.get_history_by_module),
    url(r'^get/module_svn_history',views.get_module_svn_history), # module 时间轴
    url(r'^get/online_version',views.get_latest_online_version),
    url(r'^get/online_package',views.get_online_package_view),
    url(r'^trigger/online_package',views.trigger_online_package_view),

    url(r'^get/group',views.get_group_view),
    url(r'^get/job_info',views.get_job_info_view),
    url(r'^save/group',views.save_group_view),
    url(r'^rm/group',views.rm_group_view),
    url(r'^get/job_html',views.get_job_html_view),
    url(r'^bind/job',views.bind_job_view),
    url(r'^get/collection',views.get_collection_view),
    url(r'^save/collection',views.save_collection_view),

    url(r'^group',views.group_view),

    url(r'^pre_launch',views.pre_launch_view),

)
