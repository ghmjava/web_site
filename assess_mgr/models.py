# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.db import models
# Create your models here.

class Module(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64, verbose_name=u'名称')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')

    class Meta:
        verbose_name = u'模块表'
        verbose_name_plural = u'模块表'

class Scene(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64, verbose_name=u'名称')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')

    class Meta:
        verbose_name = u'场景表'
        verbose_name_plural = u'场景表'

class Resource(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64, verbose_name=u'名称')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')

    class Meta:
        verbose_name = u'资源表'
        verbose_name_plural = u'资源表'

class Api(models.Model):
    name = models.CharField(db_index=True, max_length=64, verbose_name=u'名称')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    desc = models.TextField(max_length=1024, null=True, blank=True, verbose_name=u'描述')
    module_id = models.IntegerField(db_index=True)
    type = models.IntegerField(db_index=True, default=0, null=True, blank=True)

    class Meta:
        verbose_name = u'接口表'
        verbose_name_plural = u'接口表'

class ApiScene(models.Model):
    api_id = models.IntegerField(db_index=True)
    scene_id = models.IntegerField(db_index=True)
    module_id = models.IntegerField(db_index=True)
    ratio = models.IntegerField( default=0, null=True, blank=True)

    class Meta:
        verbose_name = u'接口场景表'
        verbose_name_plural = u'接口场景表'

class ApiResource(models.Model):
    api_id = models.IntegerField(db_index=True)
    resource_id = models.IntegerField(db_index=True)
    type = models.IntegerField(db_index=True, default=0, null=True, blank=True)
    threshold = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        unique_together = (("api_id", "resource_id"),)
        verbose_name = u'接口资源表'
        verbose_name_plural = u'接口资源表'

class SceneRecord(models.Model):
    record_name = models.CharField(db_index=True, unique=True, max_length=128, verbose_name=u'记录名')
    module_id = models.IntegerField(db_index=True)
    scene_id = models.IntegerField(db_index=True)
    data = models.TextField(max_length=1024, null=True, blank=True, default="{}", verbose_name=u'纪录json数据')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    modify_by = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'修改者')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')

    class Meta:
        verbose_name = u'场景数据表'
        verbose_name_plural = u'场景数据表'

class ApiRecord(models.Model):
    record_name = models.CharField(db_index=True, unique=True, max_length=128, verbose_name=u'记录名')
    api_id = models.IntegerField(db_index=True)
    data = models.TextField(max_length=1024, null=True, blank=True, default="{}", verbose_name=u'纪录json数据')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    modify_by = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'修改者')
    creator = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')

    class Meta:
        verbose_name = u'单接口数据表'
        verbose_name_plural = u'单接口数据表'

class Formula(models.Model):
    record_id = models.IntegerField(db_index=True)
    resource_id = models.IntegerField(db_index=True)
    formula = models.TextField(max_length=1024, null=True, blank=True, default="{}", verbose_name=u'公式json数据')

    class Meta:
        verbose_name = u'场景资源公式'
        verbose_name_plural = u'场景资源公式'