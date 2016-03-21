# coding=utf-8
import os
from django.db import models
import conf

# Create your models here.
class ReposType(models.Model):
    name = models.CharField(max_length=16, verbose_name=u'版本库类型')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'版本库类型'
        verbose_name_plural = u'版本库类型'


class Module(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'模块名')
    repos_type = models.ForeignKey(u'ReposType', verbose_name=u'版本库类型')
    repos_addr = models.CharField(max_length=256, verbose_name=u'svn地址')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'模块'
        verbose_name_plural = u'模块'


#class VersionType(models.Model):
#    name = models.CharField(max_length=32, verbose_name=u'版本类型')
#
#    def __unicode__(self):
#        return self.name
#
#    class Meta:
#        verbose_name = u'版本类型'
#        verbose_name_plural = u'版本类型'


class CovTask(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'任务名')
    module = models.ForeignKey(u'Module', verbose_name=u'模块')
    version = models.CharField(max_length=32, verbose_name=u'版本')
    created_by = models.CharField(max_length=16, verbose_name=u'创建人')
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    pack_state = models.CharField(max_length=16, verbose_name=u'打包状态')
    report_state = models.CharField(max_length=16, verbose_name=u'报告状态')
    last_report_time = models.DateTimeField(null=True, verbose_name=u'最近报告时间')
    last_upload_time = models.DateTimeField(null=True, verbose_name=u'最近上传时间')
    bgjob_id = models.CharField(max_length=64, null=True, verbose_name=u'后台任务ID')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'覆盖率统计任务'
        verbose_name_plural = u'覆盖率统计任务'


def get_upload_path(instance, filename):
    task = getattr(instance, 'cov_task')
    if task:
        upload_path = conf.FMT_TASK_DIR % (task.id, task.name)
    else:
        upload_path = conf.FMT_TASK_DIR % (0, u'unknow')

    return os.path.join(upload_path, u'upload', filename)


class CovData(models.Model):
    cov_task = models.ForeignKey(u'CovTask', verbose_name=u'任务')
    user_name = models.CharField(max_length=16, verbose_name=u'用户名')
    user_account = models.CharField(max_length=16, verbose_name=u'用户账号')
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    data = models.FileField(max_length=256, upload_to = get_upload_path)
    file_name = models.CharField(max_length=256, verbose_name=u'文件名')
    file_size = models.CharField(max_length=32, verbose_name=u'文件大小')
    file_md5 = models.CharField(max_length=34, verbose_name=u'文件MD5')
    cov_report = models.ForeignKey(u'CovReport', verbose_name=u'任务')

    def __unicode__(self):
        return str(self.cov_task.id) + '.' + self.user_name

    class Meta:
        verbose_name = u'覆盖率运行数据'
        verbose_name_plural = u'覆盖率运行数据'


class CovReport(models.Model):
    cov_task = models.ForeignKey(u'CovTask', verbose_name=u'任务')
    name = models.CharField(max_length=16, verbose_name=u'用户名')
    account = models.CharField(max_length=16, verbose_name=u'用户账号')
    state = models.CharField(max_length=16, verbose_name=u'状态')
    cov_class = models.CharField(max_length=8, verbose_name=u'类覆盖率')
    cov_method = models.CharField(max_length=8, verbose_name=u'方法覆盖率')
    cov_block = models.CharField(max_length=8, verbose_name=u'块覆盖率')
    cov_line = models.CharField(max_length=8, verbose_name=u'行覆盖率')

    def __unicode__(self):
        return str(self.cov_task.id) + '.' + str(self.account)

    class Meta:
        verbose_name = u'覆盖率报告'
        verbose_name_plural = u'覆盖率报告'


#class CovReportEvent(models.Model):
#    event = models.CharField(max_length=16, verbose_name=u'报告事件')
#    cov_report = models.ForeignKey(u'CovReport', verbose_name=u'任务报告')
#    cov_data = models.ForeignKey(u'CovData', null=True, on_delete=models.SET_NULL, verbose_name=u'分析文件')

