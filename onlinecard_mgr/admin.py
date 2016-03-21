# coding:utf8
'''
Created on 2015-12-02

@author: xuemengwang
'''

from django.contrib import admin
import models

admin.site.register(models.ProductCard)
admin.site.register(models.GroupVersion)
admin.site.register(models.Location)
admin.site.register(models.OnlineCard)
admin.site.register(models.GroupJobRecordRelation)
admin.site.register(models.SvnLog)
admin.site.register(models.AgileConfig)