# encoding: utf-8
# Django settings for pastoral project.
from datetime import timedelta

import os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'rapidsms',
    #     'USER': 'postgres',
    #     'PASSWORD': 'qdacau5w',
    #     'HOST': 'localhost',
    #     'PORT': '',
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pastoral.db')
    }

}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's2*0hjm_%otke=64+ao__#u8sqtzrdf6%5+qph2+i#+(tm*vti'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ROOT_URLCONF = 'pastoral.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'pastoral/templates'),
    os.path.join(PROJECT_PATH, 'forms/templates'),
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
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
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'basic',
            'filename': os.path.join(PROJECT_PATH, 'rapidsms.log'),
        },
        'app_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'basic',
            'filename': os.path.join(PROJECT_PATH, 'app.log'),
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pastoral': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'blockingrouter': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'celery': {
            'handlers': ['sentry'],
            'level': 'ERROR'
        }
    }
}

INSTALLED_APPS = (
    'raven.contrib.django.raven_compat',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # External apps
    "django_nose",
    "djtables",
    "selectable",
    "django_tables2",
    "rapidsms",
    "rapidsms.backends.database",
    "rapidsms.contrib.handlers",
    #"rapidsms.contrib.default",
    "registro",
    "httptester",
    #"rapidsms.contrib.locations",
    "rapidsms.contrib.messaging",
    #"rapidsms.contrib.registration",
    "rapidsms.contrib.echo",
    "rapidsms.router.celery",
    # "eav",
    "south",
    'djcelery',
    'tastypie',
    "forms",
    "web",
    "websend"
)

import djcelery

djcelery.setup_loader()
BROKER_URL = "redis://"

CELERYBEAT_SCHEDULE = {
    'cron': {
        'task': 'forms.tasks.cron',
        'schedule': timedelta(seconds=60)
    },
}

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "httptester.backend.HttpTesterCacheBackend",
    },

    "purebros": {
        "ENGINE": "purebros.outgoing.PurebrosBackend",
        "sendsms_url": "http://209.85.13.170/cprovider/cdeliver",
        "username": "pastorapid",
        "password": "pastorapid2311",
        "mt_servtype": "200001",
        "short_number": "24741"
    },
}

RAVEN_CONFIG = {
    'dsn': 'https://c3eed5e2bf3b4b719e68a73004eece43:dbace7d75ce44f08a77f3314a8d6e884@app.getsentry.com/9522',
}

RAPIDSMS_ROUTER = "rapidsms.router.celery.CeleryRouter"

# this rapidsms-specific setting defines which views are linked by the
# tabbed navigation. when adding an app to INSTALLED_APPS, you may wish
# to add it here, also, to expose it in the rapidsms ui.
RAPIDSMS_TABS = [
    ("rapidsms-dashboard", "Painel"),
    ("list_forms", "Formulários"),
    ("registro.views.message_log", "Log"),
    #("rapidsms.contrib.registration.views.registration",    "Registration"),
    #("rapidsms.contrib.messaging.views.messaging",          "Messaging"),
    #("rapidsms.contrib.locations.views.locations",          "Map"),
    #("rapidsms.contrib.scheduler.views.index",              "Event Scheduler"),
    #("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),
]

LOGIN_REDIRECT_URL = '/'

# Configuracoes iniciais para os módulos da Pastoral
CFG_BOOLEAN = 1
CFG_TEXT = 2
CFG_NUMBER = 3

DEFAULT_CONFIGURATION = {
    "Geral": {
        "retry_time": {
            "val": 30,
            "type": CFG_NUMBER,
            "label": "Tempo em segundos para tentar enviar novamente a mensagem caso o servidor de saida não responda"
        },
        "cron_time": {
            "val": 30,
            "type": CFG_NUMBER,
            "label": "Tempo em segundos que o serviço interno de cron irá ser rodado."
        },
        "max_sms_length": {
            "val": 160,
            "type": CFG_NUMBER,
            "label": "Número máximo de caracteres permitidos em um SMS."
        },
        "positive_confirmation_list": {
            "val": "1, SIM",
            "type": CFG_TEXT,
            "label": "Códigos de confirmação negativo (cancelamento)"
        },
        "negative_confirmation_list": {
            "val": "2, NAO",
            "type": CFG_TEXT,
            "label": "Códigos de confirmação positivo"
        }
    },
    "RPC": {
        "rpc_server": {
            "val": "http://fac.pastoraldacrianca.org.br/rpc",
            "type": CFG_TEXT,
            "label": "URL do servidor RPC"
        },
        "rpc_username": {
            "val": "breno",
            "type": CFG_TEXT,
            "label": "Nome de usuario para o servidor RPC"
        },
        "rpc_password": {
            "val": "cpf357",
            "type": CFG_TEXT,
            "label": "Senha para o servidor RPC"
        },
        "rpc_authenticate": {
            "val": True,
            "type": CFG_BOOLEAN,
            "label": "User autenticação no transportar RPC?"
        }
    },
    "Respostas padrões": {
        "ans_incorrect_num_fields": {
            "val": "Voce enviou um numero incorreto de campos. Por favor, verifique sua tabela.",
            "type": CFG_TEXT,
            "label": "Mensagem padrão quando o número de campos é diferente do necessário."
        },
        "ans_waiting_confirmation": {
            "val": "Você enviou dados ao nosso sistema, gostaria de confirmá-los?",
            "type": CFG_TEXT,
            "label": "Mensagem de confirmação padrão."
        },
        "ans_negative_confirmation": {
            "val": "Obrigado, recebemos seu pedido de cancelamento com sucesso.",
            "type": CFG_TEXT,
            "label": "Mensagem de agradecimento padrão para confirmação negativa."
        },
        "ans_positive_confirmation": {
            "val": "Obrigado, recebemos sua confirmação com sucesso.",
            "type": CFG_TEXT,
            "label": "Mensagem de agradecimento padrão para confirmação positiva."
        },
        "message_unknown_format": {
            "val": "Desculpe, nao conseguimos processar sua mensagem.",
            "type": CFG_TEXT,
            "label": "Mensagem de erro padrão para formato não reconhecido de SMS"
        },
        "ans_unknown_confirmation": {
            "val": "Desculpe, não conseguimos entender o código de confirmação enviado, por favor use %s para confirmar, %s"
                   " para cancelar.",
            "type": CFG_TEXT,
            "label": "Mensagem de erro padrão para código de confirmação não reconhecido"
        },
        "use_thanks_message": {
            "val": True,
            "type": CFG_BOOLEAN,
            "label": "Usar mensagem de agradecimento de envio para formulários sem confirmação?"
        },
        "ans_confirmed": {
            "val": "Muito obrigado, recebemos sua mensagem com sucesso.",
            "type": CFG_TEXT,
            "label": "Mensagem padrão de agradecimento a ser enviada para formulário que não requeiram confirmação e não "
                     "definam uma."
        },
    },
}

# Make django use redis for caching
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 1,
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}