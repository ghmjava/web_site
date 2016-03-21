# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.contrib import admin
import models


class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'trunk', 'branch', 'type']

admin.site.register(models.Module, ModuleAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'module_id', 'type', 'user', 'desc']

admin.site.register(models.Task, TaskAdmin)

class TaskRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'module_id', 'task_id', 'status', 'sheet_id', 'run_type', 'start_time', 'end_time']

admin.site.register(models.TaskRecord, TaskRecordAdmin)

class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'task_id', 'is_start', 'pre', 'next']

admin.site.register(models.SubTask, SubTaskAdmin)

class SubTaskRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_record_id', 'subtask_id', 'user', 'status', 'runStartTime', 'runEndTime']

admin.site.register(models.SubTaskRecord, SubTaskRecordAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'scene', 'desc']

admin.site.register(models.Job, JobAdmin)

class JobSetAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_id', 'subtask_id', 'is_start', 'next']

admin.site.register(models.JobSet, JobSetAdmin)

class JobRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_record_id', 'subtask_record_id', 'jobset_id', 'job_id', 'status', 'runStartTime', 'runEndTime']

admin.site.register(models.JobRecord, JobRecordAdmin)

class FailTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'desc']

admin.site.register(models.FailType, FailTypeAdmin)
