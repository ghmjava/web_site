__author__ = 'xuemengwang'

import logging
import json
import os
import time
import uuid
import datetime
import urllib2,cookielib
import urllib
from django.core import serializers
from django.db.models import Q,F
from django.conf import settings
from django.forms.models import model_to_dict
import public
import models
from data_mgr import models as data_mgr_models
from data_mgr import utils as data_mgr_utils
import commands
import requests
import subprocess

from web_mgr import utils as web_utils

logger = logging.getLogger("web_site.data_mgr.util")


def get_online_package_version(module):
    online_module = public.model_to_list(data_mgr_models.OnlinePackage.objects.raw("select * from data_mgr_onlinepackage where name=\"" + module +"\""))
    return online_module.get("package")


def get_module_by_opmodule(name):
    op_modules = public.model_to_list(data_mgr_models.JobInfo.objects.raw("select * from data_mgr_jobinfo where name=\"newlabs_" + name + "\"GROUP  BY  tag"))
    if len(op_modules) == 0:
        return ""
    else:
        return op_modules[0].get("tag")