"""
Django settings for bookstore project.

Este arquivo contém todas as configurações do Django para o projeto cgvBookStore.
As seções estão organizadas por funcionalidade para melhor manutenção.
"""

import os
from pathlib import Path
from decouple import config

# ==============================================================================
# CONFIGURAÇÕES BÁSICAS
# ==============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-=&+e$)$-ri&-n^q2=4gz+shsen^gn^^$@m6iww+9w5(t3&a)@&')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# ==============================================================================
# CONFIGURAÇÕES DE APLICAÇÕES
# ==============================================================================

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps Locais
    'core',
    'analytics',

    # Apps de Terceiros
    'django_bootstrap5',
    'stdimage',
    'crispy_forms',
]

# ==============================================================================
# CONFIGURAÇÕES DE MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom Middleware
    'analytics.middleware.LoggingMiddleware',
    'analytics.middleware.CustomSessionMiddleware',
    'analytics.middleware.AnalyticsMiddleware',
    'analytics.middleware.ImprovedAutoLogoutMiddleware',
]

# ==============================================================================
# CONFIGURAÇÕES DE TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

# ==============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'backups' / 'database' / 'current' / 'db.sqlite3',
    }
}

# Configuração de cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 7 * 24 * 60 * 60,  # 7 dias
        'KEY_PREFIX': 'bookstore',
    }
}

# ==============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ==============================================================================
# CONFIGURAÇÕES DE INTERNACIONALIZAÇÃO
# ==============================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS E MEDIA
# ==============================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO E SESSÃO
# ==============================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/'

AUTO_LOGOUT_DELAY = 1800  # 30 minutos em segundos

# Configurações de Sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_COOKIE_NAME = 'sessionid'

# ==============================================================================
# CONFIGURAÇÕES DE EMAIL
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = [
    ('Claudio Vargas', 'claudio.g.vargas@gmail.com'),
    ('Anna Clara S. Vargas', 'anna.cs.vargas@outlook.com')
]

# ==============================================================================
# CONFIGURAÇÕES DE THIRD-PARTY APPS
# ==============================================================================

# Google Books API
GOOGLE_BOOKS_API_KEY = config('GOOGLE_BOOKS_API_KEY')

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ==============================================================================
# CONFIGURAÇÕES DE LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cgvbookstore.log'),
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'book_actions': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'analytics': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ==============================================================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# OUTRAS CONFIGURAÇÕES
# ==============================================================================

ROOT_URLCONF = 'bookstore.urls'
WSGI_APPLICATION = 'bookstore.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Criação do diretório de logs
import os
LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'cgvbookstore.log')
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)