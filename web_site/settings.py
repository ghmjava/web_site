#coding:utf8
# Django settings for web_site project.
import sys
import logging
import os


#######################################self define##################################
__dir__ = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(__dir__, "..")
VAR_DIR = os.path.join(PROJECT_ROOT, "var")
DATA_DIR = os.path.join(VAR_DIR, "data")
LOG_DIR = os.path.join(VAR_DIR, "log")

#######################################system define################################


DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

AUTOCOMMIT = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'auto_test',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'auto-test',                  # Not used with sqlite3.
        'HOST': '10.8.4.97',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DATA_DIR, ".medical.sqlite.db"),                      # Or path to database file if using sqlite3.
    }
}
'''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(VAR_DIR, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(VAR_DIR, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ws8v6q^6he^6=g2*b0&amp;3h2emo@$!u&amp;ln622&amp;d@q(902es2rr2e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'web_site.urls'
SESSION_COOKIE_AGE = 60*60*24
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'web_site.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(VAR_DIR, "templates"),
    # add for cov
    os.path.join(PROJECT_ROOT, "cov/templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

INSTALLED_APPS = tuple(list(INSTALLED_APPS) + [
   # 'suit',
    'django.contrib.admin',
    'web_mgr',
    'data_mgr',
    'exception_mgr',
    'job_mgr',
    'ci_mgr',
    'assess_mgr',
    'onlinecard_mgr',
    # add for cov
    #'cov',
    #'django_rq',
    #'rest_framework'
])

REPORT_BUILDER_GLOBAL_EXPORT = True
DATETIME_FORMAT = ('Y-m-d H:i:s')
SUIT_CONFIG = {
        # header
        'ADMIN_NAME': u'测试服务化平台',
        'HEADER_DATE_FORMAT': 'Y-m-d',
        'HEADER_TIME_FORMAT': 'H:i:s',
        'SEARCH_URL': '/admin',
        'MENU_OPEN_FIRST_CHILD': True, # Default True
        'LIST_PER_PAGE': 50
}

logging.basicConfig(
    level = logging.ERROR,
    format = '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] [Line:%(lineno)d]: %(message)s \n',
    filename = os.path.join(LOG_DIR, "run.log"),
)

# add for cov
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 10,
        'DEFAULT_TIMEOUT': 1000,
        #'PASSWORD': 'local_redis',
        #'ASYNC': False,
    },
}
RQ_SHOW_ADMIN_LINK = True
