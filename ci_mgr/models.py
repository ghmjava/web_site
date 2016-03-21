# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Module(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64, verbose_name=u'名称')
    trunk = models.CharField(max_length=512, verbose_name=u'svn主干')
    branch = models.CharField(max_length=512, verbose_name=u'svn分支')
    type = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'类型')

    class Meta:
        verbose_name = u'Module表'
        verbose_name_plural = u'Module表'

class Task(models.Model):
    name = models.CharField(db_index=True, max_length=64, verbose_name=u'名称')
    module_id = models.IntegerField(db_index=True, verbose_name=u'module_id')
    type = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'类型')
    user = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')
    trigger_job = models.TextField(max_length=1024, null=True, blank=True, default="[]", verbose_name=u'触发job')
    timer = models.TextField(null=True, blank=True, default="{}", verbose_name=u'定时器')

    class Meta:
        verbose_name = u"Task表"
        verbose_name_plural = u'Task表'

class TaskRecord(models.Model):
    module_id = models.IntegerField(db_index=True)
    task_id = models.IntegerField(db_index=True)
    status = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'状态')
    options = models.TextField(null=True, blank=True, verbose_name=u'自定义')
    sheet_id = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u"提测单id")
    run_type = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'触发类型')
    start_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=u'开始时间')
    end_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name=u'结束时间')
    params = models.TextField(null=True, blank=True, default="{}", verbose_name=u'全局参数')

    class Meta:
        verbose_name = u"TaskRecord表"
        verbose_name_plural = u'TaskRecord表'

class SubTask(models.Model):
    name = models.CharField(db_index=True, max_length=64, verbose_name=u'名称')
    task_id = models.IntegerField(db_index=True, verbose_name=u'task_id')
    type = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'类型')
    is_start = models.BooleanField(db_index=True, default=True, verbose_name=u'是否为起始')
    pre = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'前置子任务id')
    next = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'后置子任务id')
    user = models.CharField(db_index=True, max_length=128, verbose_name=u'创建者')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')

    class Meta:
        verbose_name = u"SubTask表"
        verbose_name_plural = u'SubTask表'

class SubTaskRecord(models.Model):
    module_id = models.IntegerField(db_index=True)
    task_id = models.IntegerField(db_index=True)
    task_record_id = models.IntegerField(db_index=True)
    subtask_id = models.IntegerField(db_index=True)
    machine_id = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'环境id')
    sheet_id = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u"提测单id")
    user = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    branch = models.CharField(db_index=True, null=True, blank=True, max_length=64, verbose_name=u'branch name')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'运行开始时间')
    runStartTime = models.DateTimeField(null=True, blank=True, verbose_name=u'运行开始时间')
    runEndTime = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=u'运行结束时间')
    status = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'状态')
    options = models.TextField(null=True, blank=True, verbose_name=u'自定义')

    class Meta:
        verbose_name = u"SubTaskRecord表"
        verbose_name_plural = u'SubTaskRecord表'


class Job(models.Model):
    name = models.CharField(db_index=True, max_length=128, verbose_name=u'名称')
    jenkins_name = models.CharField(unique=True, max_length=128, verbose_name=u'jenkins的名字')
    module_id = models.IntegerField(db_index=True)
    type = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'类型')
    scene = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'场景')
    desc = models.CharField(db_index=True, null=True, blank=True, max_length=1024, verbose_name=u'说明')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    user = models.CharField(db_index=True, max_length=128, verbose_name=u'创建者')
    job_detail = models.TextField(null=True, blank=True, verbose_name=u'job详情')

    class Meta:
        verbose_name = u"Job表"
        verbose_name_plural = u'Job表'


class JobSet(models.Model):
    job_id = models.IntegerField(db_index=True)
    subtask_id = models.IntegerField(db_index=True)
    is_start = models.BooleanField(db_index=True, default=True, verbose_name=u'是否为起始')
    pre = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'前置job')
    next = models.CharField(null=True, blank=True, max_length=128, default="[]", verbose_name=u'后置job列表')

    class Meta:
        unique_together = (("subtask_id", "job_id"),)
        verbose_name = u"Job集合表"
        verbose_name_plural = u'Job集合表'

class JobRecord(models.Model):
    task_record_id = models.IntegerField(db_index=True)
    subtask_record_id = models.IntegerField(db_index=True)
    module_id = models.IntegerField(db_index=True)
    jobset_id = models.IntegerField(db_index=True)
    job_id = models.IntegerField(db_index=True)
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    runStartTime = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=u'运行开始时间')
    runEndTime = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=u'运行结束时间')
    status = models.IntegerField(db_index=True, null=True, blank=True, verbose_name=u'状态')
    is_start = models.BooleanField(db_index=True, default=True, verbose_name=u'是否为起始')
    user = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'标注者')
    reason = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'失败原因')
    fail_type = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'失败类型')
    param = models.TextField(null=True, blank=True, verbose_name=u'参数')
    options = models.TextField(null=True, blank=True, default="{}", verbose_name=u'自定义')

    class Meta:
        verbose_name = u"JobRecord表"
        verbose_name_plural = u'JobRecord表'

class FailType(models.Model):
    name = models.CharField(db_index=True, max_length=128, verbose_name=u'名称')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')
