# coding=utf-8
from web_site import settings
import public

# 环境变量配置
TASK_ROOT = u"%s/cov/tasks" %settings.MEDIA_ROOT
ANDROID_BUILD_TOOLS = u'/home/work/zhilird/android_tools'
ENV = u'linux'

# 字符串格式化模版配置
FMT_TASK_DIR = TASK_ROOT + u'/task_%s_%s'
FMT_REPORT_URL = public.WEB_URL + u'media/cov/tasks/task_%d_%s/report/%s/index.html'