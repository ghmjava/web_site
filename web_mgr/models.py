# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserInfo(models.Model):
    mail = models.CharField(unique=True, max_length=128, verbose_name=u'邮箱')
    name = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'姓名')
    depart = models.CharField(db_index=True, max_length=128, blank=True, null=True, verbose_name=u'部门')
    first = models.DateTimeField(auto_now_add=True, verbose_name=u'首次登陆时间')
    latest = models.DateTimeField(auto_now=True, verbose_name=u'最新登陆时间')
    times = models.IntegerField(default=0, null=True, blank=True, verbose_name=u'登陆次数')
    options = models.TextField(blank=True, null=True, verbose_name=u'自定义')
    auth = models.IntegerField(db_index=True, default=0)

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = u"用户信息"

class Authorization(models.Model):
    user_id = models.IntegerField(db_index=True, default=0, verbose_name=u'用户id')
    work_id = models.IntegerField(db_index=True, default=0, verbose_name=u'业务id')
    admin = models.IntegerField(db_index=True, default=0, verbose_name=u'管理员')
    write = models.IntegerField(db_index=True, default=0, verbose_name=u'写权限')

    class Meta:
        unique_together = (("user_id", "work_id"),)
        verbose_name = u"用户权限"
        verbose_name_plural = u"用户权限"