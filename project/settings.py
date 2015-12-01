# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
APPROOT = os.path.dirname(os.path.dirname(__file__)) + os.sep

from django.utils.translation import ugettext_lazy as _

# local_settings should define a 'options' dictionary with
# configuration values.
try:
    from local_settings import options
except ImportError:
    options = {}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = options.get('secret_key', 'no_secret_at_all_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = options.get('development', False)
TEMPLATE_DEBUG = options.get('development', False)

ALLOWED_HOSTS = []

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

# Application definition
INSTALLED_APPS = [
    'coco',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taggit',
    'sorl.thumbnail',
    'rest_framework',
    'crispy_forms',

    # The Django sites framework is required by allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.twitter',
    #'allauth.socialaccount.providers.vimeo',
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
#    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)
SITE_ID = 1

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
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = APPROOT + 'static/'

# Allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

if options.get('raven_dsn'):
    INSTALLED_APPS += ( 'raven.contrib.django.raven_compat', )

if options.get('development'):
    INSTALLED_APPS += ( 'django_extensions', )

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}
