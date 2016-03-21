# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.contrib import admin
import models


class JobInfoAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ['id', 'name', 'pre_id', 'url', 'update_time', 'status']

admin.site.register(models.JobInfo, JobInfoAdmin)
