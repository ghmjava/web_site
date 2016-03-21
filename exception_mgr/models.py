# coding:utf8
'''
Created on 2015-03-18

@author: liliurd
'''

from django.db import models

# Create your models here.
class SeException(models.Model):    
    func_name = models.CharField(max_length=50,
                                 verbose_name=u'函数名')
    options = models.TextField(default="",
                               null=True,
                               blank=True,
                               verbose_name=u'自定义错误')
    exception = models.TextField(default="",
                                 null=True,
                                 blank=True,
                                 verbose_name=u'系统异常信息')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=u'时间')
    
    def __unicode__(self):
        e = "id:%d, operation:%s, define:%s, create_time:%s" % \
        (self.id, self.func_name, self.options, str(self.create_time))
        return e
    
    class Meta:
        verbose_name = u"错误记录表"
        verbose_name_plural = u"错误记录表"
