# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.contrib import admin
import models


class UserInfoAdmin(admin.ModelAdmin):
    ordering = ['-latest']
    list_display = ['id', 'name', 'depart', 'first', 'latest', 'times']
    search_fields = ['name', 'mail']

admin.site.register(models.UserInfo, UserInfoAdmin)

