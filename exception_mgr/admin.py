#coding:utf8
from django.contrib import admin
from models import SeException

class SeExceptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'create_time','func_name',)
    search_fields = ('func_name',)
    date_hierarchy = 'create_time'
    list_filter = ['create_time']
admin.site.register(SeException, SeExceptionAdmin)

