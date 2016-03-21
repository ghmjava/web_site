# coding=utf-8
#import threading
import os
import datetime

from django_rq import job

import models
import compiler
import conf
import emma_result_parser as emmarp

def enum(**enums):
    return type('Enum', (), enums)

def job_compile(kwargs):
    if not kwargs.has_key(u'task_id'):
        return

    task_id = kwargs[u'task_id']
    tasks = models.CovTask.objects.filter(id=task_id)
    if 0 >= len(tasks):
        return

    task = tasks[0]

    module = task.module

    task.pack_state = u'doing'
    task.save()

    cmpler = compiler.Compiler(module.name, module.repos_type.name, module.repos_addr)
    cmpler.init_work_space(conf.FMT_TASK_DIR %(task.id, task.name))
    ret = cmpler.download_code(task.version)
    if 0 != ret:
        task.pack_state=u'failed'
        task.save()
        return

    ret = cmpler.compile()
    if 0 != ret:
        task.pack_state=u'failed'
        task.save()
        return

    task.pack_state=u'success'
    task.bgjob_id = u''
    task.save()

    return

#def job_analysis(task_id, task_name, user_account, file_path):
#    tasks = models.CovTask.objects.filter(pk=task_id)
#    if 0 >= len(tasks):
#        return
#    task = tasks[0]
#    covdatas = models.CovData.objects.filter(cov_task=task, user_account = user_account)
#    if 0 >= len(covdatas):
#        return
#
#    android_path = u'~/tools/android-sdk-macosx'
#    task_root = u'%s/cov/tasks/task_%s_%s' %(settings.PROJECT_ROOT, task_id, task_name)
#    src_path = task_root + u'/out/src/'
#    em_path = task_root + u'/out/coverage.em'
#    ec_path = file_path
#    out_path = u'/Users/MLS/tools/nginx-1.8.0/html/tasks/task_%s_%s/%s' %(task_id, task_name, user_account)
#
#    shell = u'java -cp %s/tools/lib/emma.jar emma report -r html -in %s -in %s -sp %s -Dreport.html.out.file=%s/index.html'\
#            % (android_path, em_path, ec_path, src_path, out_path)
#    os.system(shell)
#
#def job_gen_report(cov_report_id):
#    cov_reports = models.CovReport.objects.filter(id=cov_report_id)
#    if 0 >= len(cov_reports):
#        return 0
#    cov_report = cov_reports[0]
#
#    covdatas = cov_report.covdata_set.all()
#    if 0 == len(covdatas):
#        return 0
#
#    path = u"%s/cov/tasks/task_%s_%s" %(settings.PROJECT_ROOT, cov_report.cov_task.id, cov_report.cov_task.name)
#    shell = u'cd %s && java -cp ~/tools/android-sdk-macosx/tools/lib/emma.jar emma merge -input ' % path
#    ecs_root = os.path.join(path, u'ecs')
#    ecs_curr = os.path.join(ecs_root, cov_report.account)
#    ecs_file = os.path.join(ecs_curr, cov_report.account + u'.ec')
#    ret = os.system("rm -rf %s" %ecs_file)
#    ret = os.system("mkdir -p %s" %ecs_curr)
#
#    ecs = []
#    for each in covdatas:
#        ecs.append(each.cov_data.data.file.name)
#
#    shell += u','.join(ecs) + u' -out %s' %ecs_file
#
#    ret = os.system(shell)
#
#    return ret
#
#def job_gen_report_for_new_events(cov_report_id):
#    cov_reports = models.CovReport.objects.filter(id=cov_report_id)
#    if 0 >= len(cov_reports):
#        return
#
#    cov_report = cov_reports[0]
#    cov_report_events = cov_report.covreportevent_set.all()
#    if 0 >= len(cov_report_events):
#        return
#
#    cov_report.state = u'doing'
#    cov_report.save()
#
#    path = u"%s/cov/tasks/task_%s_%s" %(settings.PROJECT_ROOT, cov_report.cov_task.id, cov_report.cov_task.name)
#    shell = u'cd %s && java -cp ~/tools/android-sdk-macosx/tools/lib/emma.jar emma merge -input ' % path
#
#    ecs_root = os.path.join(path, u'ecs')
#    ecs_curr = os.path.join(ecs_root, cov_report.account)
#    ecs_file = os.path.join(ecs_curr, cov_report.account + u'.ec')
#    ecs = []
#    ret = os.system("ls %s" %ecs_file)
#    if 0 == ret:
#        ecs.append(ecs_file)
#    else:
#        if 0 != os.system("ls %s" %ecs_curr):
#            os.system("mkdir -p %s" %ecs_curr)
#    for each in cov_report_events:
#        if each.event == u'del_upload':
#            cov_report_events.delete()
#            ret = job_gen_report(cov_report_id)
#            return ret
#        ecs.append(each.cov_data.data.file.name)
#
#    shell += u','.join(ecs) + u' -out %s' %ecs_file
#
#    ret = os.system(shell)
#    if 0 != ret:
#        job_gen_report.delay(cov_report_id)
#        return
#
#    cov_report_events.delete()
#
#    if not cov_report.covreportevent_set.first():
#        cov_report.state = u'done'
#        cov_report.save()

def job_generate_report_for_group(task, account, cov_datas):
    if 0 == len(cov_datas):
        return 0

    # 初始化环境变量
    android_root = conf.ANDROID_BUILD_TOOLS + u'/android-sdk-macosx'
    task_root = conf.FMT_TASK_DIR %(task.id, task.name)
    src_dir = os.path.join(task_root, u'out', u'src')
    em_file = os.path.join(task_root, u'out', u'coverage.em')
    ec_dir = os.path.join(task_root, u'ecs', account)
    ec_file = os.path.join(ec_dir, account + u'.ec')
    out_dir = u'%s/report/%s' %(task_root, account)

    # 获取report对象
    if u'total' != account:
        cov_report = cov_datas[0].cov_report
    else:
        cov_reports = task.covreport_set.filter(account=u'total')
        if 0 < len(cov_reports):
            cov_report = cov_reports[0]
        else:
            cov_report = models.CovReport()
            cov_report.cov_task = task
            cov_report.account = account
            cov_report.name = account

    cov_report.state = u'generating'
    cov_report.save()

    # merge ec 文件
    ecs = []
    for cov_data in cov_datas:
        ecs.append(cov_data.data.file.name)

    shell = u'rm -rf %s' %ec_dir
    shell += u' && mkdir -p %s ' %ec_dir
    shell += u' && java -cp %s/tools/lib/emma.jar emma merge -input ' %android_root
    shell += u','.join(ecs)
    shell += u' -out %s' %ec_file
    ret = os.system(shell)
    if 0 != ret:
        print "job_generate_report_for_group merge .ecs failed <task_id: %d, account: %s>" %(task.id, account)
        cov_report.state = u'failed'
        cov_report.save()
        return ret
    else:
        print "job_generate_report_for_group merge .ecs success <task_id: %d, account: %s>" %(task.id, account)

    # 生成报告
    os.system(u'rm -rf %s' %out_dir)
    os.system(u'mkdir -p %s' %out_dir)
    shell = u'java -cp %s/tools/lib/emma.jar emma report -r html -in %s -in %s -sp %s -Dreport.html.out.file=%s/index.html'\
            % (android_root, em_file, ec_file, src_dir, out_dir)
    ret = os.system(shell)
    if 0 != ret:
        print "job_generate_report_for_group generate failed <task_id: %d, account: %s>" %(task.id, account)
        cov_report.state = u'failed'
        cov_report.save()
        return ret
    else:
        print "job_generate_report_for_group generate success <task_id: %d, account: %s>" %(task.id, account)

    # 保存summary info
    ret = emmarp.parse_summary_info_by_html(u'%s/index.html' %out_dir)
    if None != ret:
        print ret
        cov_report.cov_class = ret[u'class_cov']
        cov_report.cov_method = ret[u'method_cov']
        cov_report.cov_block = ret[u'block_cov']
        cov_report.cov_line = ret[u'line_cov']

    cov_report.state = u'success'
    cov_report.save()

    return 0

def job_generate_report(kwargs):
    if not kwargs.has_key(u'task_id'):
        return 0

    task_id = kwargs[u'task_id']

    tasks = models.CovTask.objects.filter(id=task_id)
    if 0 >= len(tasks):
        return 0

    task = tasks[0]
    task.report_state = u'generating'
    task.last_report_time = datetime.datetime.now()
    task.save()

    cov_datas = task.covdata_set.all()
    cov_datas_group_by_user = {}
    for cov_data in cov_datas:
        account = cov_data.user_account
        if not cov_datas_group_by_user.has_key(account):
            cov_datas_group_by_user[account] = []

        cov_datas_group_by_user[account].append(cov_data)

    # 生成user报告
    for account in cov_datas_group_by_user:
        job_generate_report_for_group(task, account, cov_datas_group_by_user[account])

    # 生成总报告
    job_generate_report_for_group(task, u'total', cov_datas)

    task.report_state = u'success'
    task.save()

    return 0

job_type = enum(
    compile = 0,
    analysis = 1,
    gen_report = 2,
)

job_func = {
    job_type.compile : job_compile,
    #job_type.analysis : job_analysis,
    job_type.gen_report : job_generate_report,
}

@job
def run_asyn(type, args=(), kwargs={}):

    if not job_func.has_key(type):
        return 1

    ret = job_func[type](kwargs)
    #t = threading.Thread(target=job_func[type], args=args, kwargs=kwargs)
    #t.start()
    #t.join()

    return ret

def run_sync(type, args=(), kwargs={}):
    pass
