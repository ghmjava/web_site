# coding=utf-8
import os
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.core.urlresolvers import reverse

import public
from .models import *
from .forms import *
import conf
import job
import utils

# Create your views here.
@public.auth_user
def index(request):
    tasks = CovTask.objects.all()
    context = {'tasks': tasks[::-1]}
    return render(request, 'cov_index.html', context)

@public.auth_user
def new(request):
    if request.method == 'POST':
        module = Module.objects.get(name=request.POST.get(u'module'))
        task = CovTask(name=request.POST.get(u'task'),
                       module=module,
                       version=request.POST.get(u'version'),
                       created_by=request.session[u'django_name'],
                       pack_state=u'init',
                       report_state=u'init')
        task.save()

        ret = job.run_asyn.delay(type=job.job_type.compile, kwargs={u'task_id': task.id})

        if ret.id and 0 < len(ret.id):
            task.bgjob_id = ret.id
            task.save()

        return HttpResponseRedirect(reverse('cov:detail', args=(task.id,)))
    else:
        task_name_def = u'Task_' + datetime.datetime.now().strftime(u'%Y%m%d%H%M%S');
        modules = Module.objects.all()
        return render(request, 'cov_new.html', {'task_name_def': task_name_def, 'modules': modules})

@public.auth_user
def detail(request, task_id):
    task = CovTask.objects.get(pk=task_id)
    module = Module.objects.get(name=task.module)

    return render(request, 'cov_detail.html', {'task': task, 'module': module})

@public.auth_user
def download_packet(request, task_id):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    task = CovTask.objects.get(pk=task_id)
    task_root = conf.FMT_TASK_DIR %(task.id, task.name)
    the_file_name = os.path.join(task_root, u'out', u'WelcomeActivity-instrumented.apk')
    #the_file_name = os.path.join(task_root, u'out', u'WelcomeActivity-debug.apk')
    #the_file_name = os.path.join(task_root, u'out', u'WelcomeActivity-release.apk')
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = u'application/octet-stream'
    response['Content-Disposition'] = u'attachment;filename="{0}"'.format(u'Meilishuo_%s.apk' %task.name)

    return response

@public.auth_user
def upload(request, task_id):
    task = CovTask.objects.get(id=task_id)
    if request.method == 'POST':
        uf = UploadForm(request.POST,request.FILES)
        if uf.is_valid():
            task.last_upload_time = datetime.datetime.now()
            task.save()

            cov_reports = CovReport.objects.filter(cov_task=task, account=request.session[u'django_mail'].split('@')[0])
            if 0 >= len(cov_reports):
                cov_report = CovReport()
                cov_report.cov_task = task
                cov_report.name = request.session[u'django_name']
                cov_report.account = request.session[u'django_mail'].split('@')[0]
                cov_report.state = u'init'
                cov_report.cov_class = u'-'
                cov_report.cov_method = u'-'
                cov_report.cov_block = u'-'
                cov_report.cov_line = u'-'
                cov_report.save()
            else:
                cov_report = cov_reports[0]

            cov_data = CovData()
            cov_data.cov_task = task
            cov_data.user_name = request.session[u'django_name']
            cov_data.user_account = request.session[u'django_mail'].split('@')[0]
            cov_data.data = uf.cleaned_data['data']
            cov_data.file_name = cov_data.data.name
            cov_data.cov_report = cov_report
            cov_data.save()
            cov_data.file_md5 = utils.get_md5(cov_data.data.file.name)
            cov_data.save()

            return render(request, 'cov_upload.html', {'task':task, 'uf': uf, 'op': u'success'})
        else:
            return render(request, 'cov_upload.html', {'task':task, 'uf': uf, 'op': u'failed'})
    else:
        uf = UploadForm()
        return render(request, 'cov_upload.html', {'task':task, 'uf': uf, 'op': u'upload'})

@public.auth_user
def delete_upload(request, task_id, upload_id):
    cov_datas = CovData.objects.filter(id=upload_id)
    if 0 == len(cov_datas):
        return HttpResponseRedirect(reverse('cov:detail', args=(task_id,)))

    cov_data = cov_datas[0]
    cov_data.cov_task.last_upload_time = datetime.datetime.now()
    cov_data.cov_task.save()
    os.system("rm -rf %s" %cov_data.data.name)
    cov_data.delete()

    return HttpResponseRedirect(reverse('cov:detail', args=(task_id,)))

@public.auth_user
def gen_report(request, task_id):
    task = CovTask.objects.get(pk=task_id)
    task.report_state=u'begining'
    task.save()

    cov_reports = task.covreport_set.filter(account=u'total')
    if 0 >= len(cov_reports):
        cov_report = CovReport()
        cov_report.cov_task = task
        cov_report.account = u'total'
        cov_report.name = u'total'
        cov_report.state = u'init'
        cov_report.cov_class = u'-'
        cov_report.cov_method = u'-'
        cov_report.cov_block = u'-'
        cov_report.cov_line = u'-'
        cov_report.save()

    cov_reports = task.covreport_set.all()
    for cov_report in cov_reports:
        cov_report.cov_class = u'-'
        cov_report.cov_method = u'-'
        cov_report.cov_block = u'-'
        cov_report.cov_line = u'-'
        cov_report.state = u'begining'
        cov_report.save()

    job.run_asyn.delay(type=job.job_type.gen_report, kwargs={'task_id': task.id})
    return HttpResponseRedirect(reverse('cov:results', args=(task.id,)))

@public.auth_user
def results(request, task_id):
    if request.method != 'GET':
        return

    task = CovTask.objects.get(pk=task_id)

    cov_reports = task.covreport_set.filter(account=u'total')
    if 0 < len(cov_reports):
        cov_report = cov_reports[0]
    else:
        cov_report = None

    return render(request, 'cov_results.html', {'task': task, 'total_report':cov_report})

@public.auth_user
def results_user(request, task_id, user_account):
    task = CovTask.objects.get(pk=task_id)
    if u'total' == user_account:
        ifm_src = conf.FMT_REPORT_URL %(task.id, task.name, user_account)
        name = user_account
    else:
        covdatas = task.covdata_set.filter(user_account=user_account)
        if 0 >= len(covdatas):
            return
        covdata = covdatas[0]
        name = covdata.user_name
        ifm_src = conf.FMT_REPORT_URL %(task.id, task.name, covdata.user_account)

    return render(request, 'cov_results_user.html', {'task': task, 'name': name, 'ifm_src': ifm_src})

@public.auth_user
def module(request):
    modules = Module.objects.all()
    context = {'modules': modules}
    return render(request, 'cov_module_list.html', context)

@public.auth_user
def new_module(request):
    if request.method == 'POST':
        repos_types = ReposType.objects.filter(name = request.POST.get('repos_type'))
        if 0 >= repos_types:
            repos_type = ReposType()
            repos_type.name = request.POST.get('repos_type')
            repos_type.save()
        else:
            repos_type = repos_types[0]

        module = Module()
        module.name = request.POST.get('module')
        module.repos_type = repos_type
        module.repos_addr = request.POST.get('repos_addr')
        module.save()
        return HttpResponseRedirect(reverse('cov:module'))
    else:
        return render(request, 'cov_module_new.html')