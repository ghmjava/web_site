# coding:utf8
'''
Created on 2015-02-14

@author: liliurd
'''

from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Dashboard(models.Model):
    env = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'环境')
    type = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'类型')
    scene = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'场景')
    interface = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'接口')
    runStartTime = models.DateTimeField(db_index=True, verbose_name=u'运行开始时间')
    runEndTime = models.DateTimeField(db_index=True, verbose_name=u'运行结束时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义参数')

    def __unicode__(self):
        return self.env

    class Meta:
        verbose_name = u"仪表盘"
        verbose_name_plural = u"仪表盘"


class Interface(models.Model):
    desc = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'描述')
    is_promotion = models.BooleanField(db_index=True, default=False, verbose_name=u'是否大促')
    path = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'路径')
    domain = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'域名')
    type = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'类型')
    params = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'参数')
    expectation = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'预期')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义参数')

    def __unicode__(self):
        return self.desc

    class Meta:
        verbose_name = u"接口表"
        verbose_name_plural = u"接口表"


class Promotion(models.Model):
    desc = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'描述')
    module = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u"模块")
    create = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义参数')

    def __unicode__(self):
        return self.desc

    class Meta:
        verbose_name = u"大促列表"
        verbose_name_plural = u"大促列表"


class PromotionRecord(models.Model):
    description = models.CharField(null=True, blank=True, max_length=512, verbose_name=u'描述')
    promotion = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'大促id')
    interface = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'接口')
    index = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'序号')
    start = models.DateTimeField(db_index=True, verbose_name=u'开始时间')
    end = models.DateTimeField(db_index=True, verbose_name=u'结束时间')
    create = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义参数')

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = u"大促记录表"
        verbose_name_plural = u"大促记录表"


class SvnHistory(models.Model):
    module = models.CharField(db_index=True, max_length=128, verbose_name=u'模块名')
    create = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'创建时间')
    modify = models.IntegerField(default=3600, verbose_name=u'更改行数')
    options = models.TextField(default="{}", blank=True, null=True, verbose_name=u'自定义参数')

    def __unicode__(self):
        return self.module

    class Meta:
        verbose_name = u"上线记录表"
        verbose_name_plural = u"上线记录表"


# jichaoliu
class AutoReport(models.Model):
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'当前时间')
    jsonString = models.TextField(default="{}", blank=True, null=True, verbose_name=u'json数据')
    status = models.CharField(db_index=True, max_length=128, blank=True, null=True, verbose_name=u'状态')
    user = models.CharField(db_index=True, max_length=128, blank=True, null=True, verbose_name=u'确认人')

    class Meta:
        verbose_name = u"自动化测试报告"
        verbose_name_plural = u"自动化测试报告"


#jichaoliu
class AutoReport_pushStatus(models.Model):
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'当前时间')
    jsonString = models.TextField(default="{}", blank=True, null=True, verbose_name=u'json数据')

    class Meta:
        verbose_name = u"上线状态表"
        verbose_name_plural = u"上线状态表"


#jichaoliu
class Push_data(models.Model):
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'当前时间')
    url = models.TextField(default="{}", blank=True, null=True, verbose_name=u'数据地址')
    releaseModel = models.TextField(default="{}", blank=True, null=True, verbose_name=u'发布模块')
    content = models.TextField(default="{}", blank=True, null=True, verbose_name=u'需求内容')
    product_director = models.TextField(default="{}", blank=True, null=True, verbose_name=u'产品负责人')
    develop_director = models.TextField(default="{}", blank=True, null=True, verbose_name=u'开发负责人')

    class Meta:
        verbose_name = u"发布计划测试数据表"
        verbose_name_plural = u"发布计划测试数据表"


#jichaoliu状态回归
class StatusBack(models.Model):
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'当前时间')
    project = models.TextField(default="{}", blank=True, null=True, verbose_name=u'项目')
    success = models.TextField(default="{}", blank=True, null=True, verbose_name=u'是否成功')

    class Meta:
        verbose_name = u"上线状态回归"
        verbose_name_plural = u"上线状态回归"


#jichaoliu上线包状态
class Package_status(models.Model):
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'当前时间')
    package = models.TextField(default="{}", blank=True, null=True, verbose_name=u'包名')
    status = models.TextField(default="{}", blank=True, null=True, verbose_name=u'上线状态')

    class Meta:
        verbose_name = u"上线包状态"
        verbose_name_plural = u"上线包状态"


#yecheng
class VersionDiff(models.Model):
    module = models.CharField(max_length=128, verbose_name=u'模块名')
    day = models.CharField(max_length=128, verbose_name=u'创建日期')
    sealed = models.CharField(max_length=128, verbose_name=u'封版版本')
    newlab = models.CharField(max_length=128, verbose_name=u'newlab版本')

    def __unicode__(self):
        return self.module

    class Meta:
        verbose_name = u"纪录每天封板时newlab版本月封板版本"
        verbose_name_plural = u"封板信息表"

class JobInfo(models.Model):
    name = models.CharField(unique=True, max_length=128, verbose_name=u'名称')
    trunk = models.CharField(max_length=512, verbose_name=u'svn主干')
    branch = models.CharField(max_length=512, verbose_name=u'svn分支')
    type = models.IntegerField(db_index=True, verbose_name=u'类型')
    tag = models.CharField(max_length=128, verbose_name=u'tag 名')
    pre_job = models.CharField(db_index=True, null=True, blank=True, max_length=128, verbose_name=u'上游job名')
    next_job = models.CharField(db_index=True, null=True, blank=True,  max_length=128, verbose_name=u'下游job名')


    class Meta:
        verbose_name = u"Job信息"
        verbose_name_plural = u"Job信息"

class JobRecord(models.Model):
    mail = models.CharField(db_index=True, max_length=128, verbose_name=u'邮箱')
    view_name = models.CharField(db_index=True, max_length=128, verbose_name=u'view名')
    job_name = models.CharField(db_index=True, max_length=128, verbose_name=u'job名')
    type = models.IntegerField(db_index=True, verbose_name=u'类型')  #0:禁用 1:启用 2:触发 3:封板
    version = models.CharField(null=True, blank=True, max_length=128, verbose_name=u'分支号')
    ctime = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=u'操作时间')
    online_version = models.CharField(max_length=100, default="", verbose_name=u'生成分组版本时，线上的版本')

    class Meta:
        verbose_name = u"Job运行记录"
        verbose_name_plural = u"Job运行记录"

class Group(models.Model):
    name = models.CharField(db_index=True, max_length=2000, verbose_name=u'名称')
    desc = models.TextField(default="", blank=True, null=True, verbose_name=u'描述')
    ckpak = models.CharField(default="", max_length=200, verbose_name=u'对应的syspush平台的ck字段')

    class Meta:
        verbose_name = u"分组表"
        verbose_name_plural = u"分组表"

class GroupJob(models.Model):
    group_id = models.IntegerField(db_index=True)
    job_id = models.IntegerField(db_index=True)
    default_locations = models.CharField(max_length=100, verbose_name=u'小模块默认的机房信息') #added by xuemengwang

    class Meta:
        verbose_name = u"分组job关系表"
        verbose_name_plural = u"分组job关系表"


class OnlinePackage(models.Model):
    name = models.CharField(unique=True, max_length=128, verbose_name=u'名称')
    package = models.CharField(db_index=True, max_length=128, verbose_name=u'线上包名')

    class Meta:
        verbose_name = u"线上包表"
        verbose_name_plural = u"线上包表"

class Collection(models.Model):
    user = models.CharField(db_index=True, max_length=32, null=True, blank=True, verbose_name=u'用户')
    job_id = models.IntegerField(db_index=True)

    class Meta:
        unique_together = (("user", "job_id"),)
        verbose_name = u"个人收藏"
        verbose_name_plural = u"个人收藏"


