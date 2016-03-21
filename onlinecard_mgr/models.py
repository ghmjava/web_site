# coding:utf8
'''
Created on 2015-12-02

@author: xuemengwang
'''

from django.db import models
# Create your models here.


class ProductCard(models.Model):
    op_card_id=models.CharField(max_length=10,verbose_name=u'每个提测单id')
    module_name = models.CharField(max_length=64, verbose_name=u'模块名称')
    content = models.CharField(max_length=500, verbose_name=u'提测单内容')
    card_type = models.CharField(max_length=45, verbose_name=u'提测单类型')
    pm_owner = models.CharField(max_length=200, verbose_name=u'产品负责人')
    rd_owner = models.CharField(max_length=200, verbose_name=u'研发负责人')
    qa_owner = models.CharField(max_length=200, verbose_name=u'测试负责人')
    test_result = models.CharField(max_length=45, verbose_name=u'测试结果')
    online_suggestion = models.CharField(max_length=500, verbose_name=u'上线建议')
    online_card_id = models.IntegerField(default=0, db_index=True, verbose_name=u'此提测单属于哪个上线单')
    need_qa = models.BooleanField(default=True, verbose_name=u'是否过测试')
    endDate = models.DateTimeField(db_index=True, verbose_name=u'结束时间')
    group_id = models.IntegerField(blank=False, verbose_name=u'改提测单属于哪个分组')
    update_time=models.DateTimeField(auto_now=True, verbose_name=u'数据插入时间')

    class Meta:
        verbose_name = u'提测单表'
        verbose_name_plural = u'提测单'


class GroupVersion(models.Model):
    group_id = models.IntegerField(db_index=True, null=False, verbose_name=u'分组id')
    user_id = models.IntegerField(db_index=True, null=False, verbose_name=u'用户id')
    version_num = models.CharField(max_length=100, db_index=True, null=False, verbose_name=u'分组版本号')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    has_published = models.SmallIntegerField(default=0, verbose_name=u'是否发布')

    class Meta:
        verbose_name = u'分组版本表'
        verbose_name_plural = u'分组版本表'


class GroupJobRecordRelation(models.Model):
    """
    分组版本和小模块版本的关系表
    """
    jobrecord_id = models.IntegerField(null=False, verbose_name=u'小模块的版本id')
    groupversion_id = models.IntegerField(null=False, verbose_name=u'分组的版本id')
    locations = models.CharField(max_length=100, null=True, verbose_name=u'机房信息')

    class Meta:
        verbose_name = u'版本关系表'
        verbose_name_plural = u'版本关系表'


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'机房名称')

    class Meta:
        verbose_name = u'机房表'
        verbose_name_plural = u'机房表'

class Pushstatus(models.Model):
    nowTime=models.DateTimeField(auto_now=True, verbose_name=u'数据存储时间')
    update_Time=models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    version=models.CharField(max_length=100,verbose_name=u'版本')
    area=models.CharField(max_length=100,verbose_name=u'地区')
    endFlag=models.IntegerField(max_length=10,verbose_name=u'上线状态')


class OnlineCard(models.Model):
    """
    上线单表
    """
    group_id = models.IntegerField(default=0, verbose_name=u'分组id')
    group_version_id = models.IntegerField(default=0, verbose_name=u'分组版本id')
    module_version_ids = models.CharField(max_length=2000, verbose_name=u'小模块版本ids')
    remark = models.TextField(max_length=1000, verbose_name=u'备注')
    mails = models.CharField(max_length=200, verbose_name=u'默认知会的邮箱', default=u'auto-test@meilishuo.com,sys@meilishuo.com')
    status = models.IntegerField(default=0, verbose_name=u'上线单状态') #0:未上线；1:已上线
    user_id = models.IntegerField(default=0, verbose_name=u'创建者')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')

    class Meta:
        verbose_name = u'上线单表'
        verbose_name_plural = u'上线单表'


class SvnLog(models.Model):
    """
    svnlog表
    """
    user = models.CharField(max_length=100, verbose_name=u'提交者')
    comment = models.CharField(max_length=500, verbose_name=u'提交评论')
    job_id = models.IntegerField(verbose_name=u'模块')#这里要关联data_mgr_jobinfo 这个表
    version = models.IntegerField(verbose_name=u'svn版本')#对应的svn trunk版本号

    class Meta:
        verbose_name = u'svn记录表'
        verbose_name_plural = u'svn记录表'


class AgileConfig(models.Model):
    """
    Agile平台常用的配置表
    """
    key = models.CharField(max_length=200, null=False)
    value = models.CharField(max_length=1024)