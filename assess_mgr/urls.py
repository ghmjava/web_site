# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''


import views
import view_algo
from django.conf.urls import patterns, url



urlpatterns = patterns('',
    url(r'^$', views.assess_main_view),
    url(r'^save/module', views.save_module_view),
    url(r'^get/module', views.get_module_view),
    url(r'^save/scene$', views.save_scene_view),
    url(r'^get/scene$', views.get_scene_view),
    url(r'^save/scene_record', views.save_scene_record_view),
    url(r'^get/scene_record', views.get_scene_record_view),
    url(r'^save/resource', views.save_resource_view),
    url(r'^get/resource', views.get_resource_view),
    url(r'^save/api$', views.save_api_view),
    url(r'^get/api$', views.get_api_view),
    url(r'^save/api_resource', views.save_api_resource_view),
    url(r'^get/api_resource', views.get_api_resource_view),
    url(r'^get/api_list', views.get_api_list),

    url(r'^module$', views.module_view),
    url(r'^module_api', views.module_api_view),
    url(r'^scene', views.scene_view),
    url(r'^resource', views.resource_view),
    url(r'^api', views.api_view),
    url(r'^post/api', views.post_api_view),
    url(r'^rm/scene', views.rm_scene_view),
    url(r'^rm/resource', views.rm_resource_view),
    url(r'^rm/api', views.rm_api_view),
    url(r'^bind/api', views.bind_api_view),

    url(r'^train_algo', view_algo.train_algorithm),
    url(r'^get/algo',view_algo.set_algo_view),
    url(r'^delete/scene_record', view_algo.delete_scene_record),
    url(r'^estimate', view_algo.get_formula_by_threshold),
    url(r'^single_api', view_algo.single_api_view),
    url(r'^save/api_record', view_algo.save_single_api_record),
    url(r'^delete/api_record', view_algo.delete_single_api_record),

)


