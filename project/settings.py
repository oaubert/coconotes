# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
APPROOT = os.path.dirname(os.path.dirname(__file__)) + os.sep

import logging, copy
from django.contrib import messages
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import ugettext_lazy as _

# local_settings should define a 'options' dictionary with
# configuration values.
try:
    from local_settings import options
except ImportError:
    options = {}

# If http_proxy is specified in local_settings, use it to initialize the appropriate conf. variables
if 'http_proxy' in options:
    os.environ['https_proxy'] = os.environ['http_proxy'] = options['http_proxy']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = options.get('secret_key', 'no_secret_at_all_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = options.get('development', False)

ALLOWED_HOSTS = options.get('allowed_hosts', [])

EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = options.get('admin_email', 'webmaster@comin-ocw.org')
SERVER_EMAIL = options.get('admin_email', 'webmaster@comin-ocw.org')
EMAIL_SUBJECT_PREFIX = '[COCoNotes] '
ADMINS = [ ('Webmaster', options.get('admin_email', 'webmaster@comin-ocw.org')) ]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(APPROOT, "media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

if options.get('redis_cache'):
    # Configure session cache
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': options.get('redis_cache', 'localhost:6379'),
            'OPTIONS': {
            'DB': 1,
            },
        },
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger error'
}

# Application definition
INSTALLED_APPS = [
    'coco',
    'ajax_select',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taggit',
    'taggit_autosuggest',
    'sorl.thumbnail',
    'rest_framework',
    'crispy_forms',

    # The Django sites framework is required by allauth
    'django.contrib.sites',
    'django.contrib.humanize',
    'actstream',
    'django_cas_ng',
]
if DEBUG:
    INSTALLED_APPS.insert(-1, 'debug_toolbar')
SHELL_PLUS = "ipython"

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'coco.backends.CustomCASBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'coco.context_processors.siteinfo'
            ],
            'debug': options.get('development', False)
        },
    },
]

SITE_ID = 1

SITE_VARIANT = options.get('site_variant', '')

RAVEN_CONFIG = {
    'dsn': options.get('raven_dsn', ''),
}

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': options.get('db_engine', 'django.db.backends.sqlite3'),
        'NAME': options.get('db_name', APPROOT + 'db.sqlite3'),
        'USER': options.get('db_user', ''),
        'PASSWORD': options.get('db_password', ''),
        'HOST': options.get('db_host', ''),
        'PORT': options.get('db_port', ''),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

LANGUAGES = (
  ('fr', _('French')),
  ('en', _('English')),
)

LOCALEPATH = APPROOT + 'coco/locale/'

USE_TZ = False

# Custom URL field name for django-rest-framework:
URL_FIELD_NAME = 'href'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = APPROOT + 'static/'

# Allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

CAS_SERVER_URL = 'https://cas-ha.univ-nantes.fr/esup-cas-server/'
CAS_FORCE_CHANGE_USERNAME_CASE = 'lower'
CAS_CREATE_USER = False

if options.get('raven_dsn'):
    INSTALLED_APPS += ( 'raven.contrib.django.raven_compat', )

if options.get('development'):
    INSTALLED_APPS += ( 'django_extensions', )

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

ACTSTREAM_SETTINGS = {
    'MANAGER': 'coco.managers.ActionManager',
    # Warning: setting FETCH_RELATIONS to True will make the generic foreign key fail. Maybe an issue with using uuids?
    'FETCH_RELATIONS': False,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 1,
}

if DEBUG:
    LOGGING = copy.deepcopy(DEFAULT_LOGGING)
    LOGGING['filters']['suppress_deprecated'] = {
        '()': 'project.settings.SuppressDeprecated'
    }
    LOGGING['handlers']['console']['filters'].append('suppress_deprecated')

    class SuppressDeprecated(logging.Filter):
        def filter(self, record):
            WARNINGS_TO_SUPPRESS = [
                'RemovedInDjango19Warning'
            ]
            # Return false to suppress message.
            return not any([warn in record.getMessage() for warn in WARNINGS_TO_SUPPRESS])
