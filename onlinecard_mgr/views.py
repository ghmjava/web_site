# coding:utf8
'''
Created on 2015-12-12

@author: xuemengwang
'''

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
import public
import requests
from data_mgr import utils as data_mgr_utils
from django.core import serializers
from onlinecard_mgr import modelutils
from data_mgr import utils as data_mgr_utils


from exception_mgr.utils import catch_exception_http


def xuemengwang_test(request):
    online_package = modelutils.get_online_package2()
    # online_package = data_mgr_utils.get_online_package()

    return public.success_result_http(online_package)