# Django settings for website project.
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ALLOWED_HOSTS =                     ['btc.westiseast.co.uk', '.bitrage.io']
TIME_ZONE =                         'Europe/London'
LANGUAGE_CODE =                     'en-gb'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# MEDIA AND STATIC SETTINGS
# -------------------------------------------------------

MEDIA_ROOT =                        os.path.join(PROJECT_PATH, 'media')
MEDIA_URL =                         '/media/'
STATIC_ROOT =                       os.path.join(PROJECT_PATH, 'static')
STATIC_URL =                        '/static/'
STATICFILES_DIRS = (

)
STATICFILES_FINDERS = (
                                    'django.contrib.staticfiles.finders.FileSystemFinder',
                                    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#                                    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# Make this unique, and don't share it with anybody.
SECRET_KEY = ''


# TEMPLATE SETTINGS
# -------------------------------------------------------

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
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


TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
    os.path.join(PROJECT_PATH, 'trader/templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'website.trader.context_processors.common',
    
)

BASE_TEMPLATE =                     'base.html'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'website.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'website.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'website.trader',
    'sorl.thumbnail',
    'mathfilters',
)


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}


# REDIS STUFF
# --------------------------------------------------------------
REDIS_DB_ID = 9
SCRAPE_INTERVAL = 15


# INFO ABOUT SITES TO SCRAPE
# --------------------------------------------------------------
BITCOIN_EXCHANGES = (
    'MTGOX (GBP)',
    'MTGOX (USD)',
    'MTGOX (EUR)',
    'BITSTAMP',
    'BITTYLICIOUS',
    'BTC-E',
    'BTCTRADE',
    'HUOBI',
    'CHBTC',
    'BTCCHINA',
    'BTC38',
    '796',
    'BTER',
    'OKCOIN',
    'FxBTC',
    'RMBTB',
)


try:
    from local_settings import *
except:
    pass

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
