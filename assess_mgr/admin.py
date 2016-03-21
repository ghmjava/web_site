# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.contrib import admin
import models

class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'desc']

admin.site.register(models.Module, ModuleAdmin)

class SceneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'desc']

admin.site.register(models.Scene, SceneAdmin)

class ResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'desc']

admin.site.register(models.Resource, ResourceAdmin)

class ApiAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'module_id', 'creator', 'desc']

admin.site.register(models.Api, ApiAdmin)

class SceneRecordAdmin(admin.ModelAdmin):
    list_display = ['id','module_id', 'scene_id', 'data']

admin.site.register(models.SceneRecord, SceneRecordAdmin)

class ApiRecordAdmin(admin.ModelAdmin):
    list_display = ['id','record_name', 'api_id', 'data']

admin.site.register(models.ApiRecord, ApiRecordAdmin)
