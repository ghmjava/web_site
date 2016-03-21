# coding:utf-8

from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('web_mgr.urls')),
    url(r'^accounts/login/$', include('web_mgr.urls')),
    url(r'^web_mgr/', include('web_mgr.urls')),
    url(r'^data_mgr/', include('data_mgr.urls')),
    url(r'^job_mgr/', include('job_mgr.urls')),
    url(r'^ci_mgr/', include('ci_mgr.urls')),
    url(r'^assess_mgr/', include('assess_mgr.urls')),
    url(r'^exception_mgr/', include('exception_mgr.urls')),
    url(r'^onlinecard_mgr/', include('onlinecard_mgr.urls')),

    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
    # add for cov
    url(r'^cov/', include('cov.urls', namespace="cov")),
    (r'^django-rq/', include('django_rq.urls')),
)
