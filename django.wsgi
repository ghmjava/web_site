#-*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.dirname(__file__)

project_path= os.path.abspath(current_dir)

if project_path not in sys.path: sys.path.append(project_path)

os.environ["DJANGO_SETTINGS_MODULE"] = "web_site.settings"

#import django.core.handlers.wsgi

#application = django.core.handlers.wsgi.WSGIHandler()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
