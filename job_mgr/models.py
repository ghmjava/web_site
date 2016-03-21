# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.db import models
# Create your models here.


class JobInfo(models.Model):
    name = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'名称')
    url = models.CharField(db_index=True, null=True, blank=True, max_length=512, verbose_name=u'路径')
    flag = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'标识')
    pre_id = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'前置')
    status = models.IntegerField(db_index=True, null=True, blank=True, default=0, verbose_name=u'状态')
    user = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'创建者')
    pass_num = models.IntegerField(null=True, blank=True, default=0)
    fail_num = models.IntegerField(null=True, blank=True, default=0)
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义')

    class Meta:
        verbose_name = u"信息表"
        verbose_name_plural = u"信息表"