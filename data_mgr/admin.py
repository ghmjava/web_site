# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.contrib import admin
import models


class DashboardAdmin(admin.ModelAdmin):
    actions_on_top = True
    date_hierarchy = 'runEndTime'
    list_display = ['id', 'env', 'type', 'scene', 'interface', 'runStartTime', 'runEndTime', 'options']
    list_filter = ['env', 'type', 'scene']

admin.site.register(models.Dashboard, DashboardAdmin)


class InterfaceAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ['id', 'desc', 'domain', 'type', 'is_promotion']
    list_filter = ['type', 'is_promotion']

admin.site.register(models.Interface, InterfaceAdmin)


class PromotionAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ['id', 'desc', 'module', 'create']

admin.site.register(models.Promotion, PromotionAdmin)


class PromotionRecordAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_display = ['id', 'promotion', 'interface', 'index', 'end', 'description', 'options']

admin.site.register(models.PromotionRecord, PromotionRecordAdmin)


class SvnHistoryAdmin(admin.ModelAdmin):
    actions_on_top = True
    list_filter = ['module']
    list_display = ['id', 'module', 'modify', 'create']

admin.site.register(models.SvnHistory, SvnHistoryAdmin)

#jichaoliu
class AutoReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'status', "user"]

admin.site.register(models.AutoReport, AutoReportAdmin)

class AutoReport_pushStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'jsonString']

admin.site.register(models.AutoReport_pushStatus, AutoReport_pushStatusAdmin)


class Push_dataAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'releaseModel','develop_director']

admin.site.register(models.Push_data, Push_dataAdmin)

class StatusBackAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'project','success']

admin.site.register(models.StatusBack, StatusBackAdmin)

class Package_statusAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'package','status']

admin.site.register(models.Package_status, Package_statusAdmin)

class JobInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'trunk', 'branch', 'type', 'tag']

admin.site.register(models.JobInfo, JobInfoAdmin)

class JobRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'mail', 'view_name', 'job_name', 'type', 'version', 'ctime']

admin.site.register(models.JobRecord, JobRecordAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'desc']

admin.site.register(models.Group, GroupAdmin)




