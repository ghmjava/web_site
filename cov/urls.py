from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^new$', views.new),
    url(r'^detail/(?P<task_id>[0-9]+)$', views.detail, name='detail'),
    url(r'^download/(?P<task_id>[0-9]+)$', views.download_packet, name='download'),
    url(r'^module$', views.module, name='module'),
    url(r'^module/new$', views.new_module, name='new_module'),
    url(r'^upload/(?P<task_id>[0-9]+)$', views.upload, name='upload'),
    url(r'^gen_report/(?P<task_id>[0-9]+)$', views.gen_report, name='gen_report'),
    url(r'^detail/(?P<task_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^detail/(?P<task_id>[0-9]+)/results/(?P<user_account>[a-zA-Z0-9]+)$', views.results_user, name='results_user'),
    url(r'^detail/(?P<task_id>[0-9]+)/delete_upload/(?P<upload_id>[0-9]+)$', views.delete_upload, name='delete_upload'),
]
