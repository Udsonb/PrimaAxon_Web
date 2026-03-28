"""
Django settings for core project.
Funciona local (SQLite) e em produção (PostgreSQL via DATABASE_URL).
"""

import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-b6^(%qu(%bn@8qvl_isg7=z@uiq$=gnmp=w287#*fm1yfr0568')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.ondigitalocean.app',
    '.onrender.com',
    '.run.app',
    'primaaxon-web-355616728924.southamerica-east1.run.app',
]

CSRF_TRUSTED_ORIGINS = [
    'https://prisma-axon-system-nh8lz.ondigitalocean.app',
    'https://*.ondigitalocean.app',
    'https://primaaxon-web.onrender.com',
    'https://*.run.app',
    'https://primaaxon-web-git-355616728924.southamerica-east1.run.app',
    'https://primaaxon-web-git-6tt7m7k6sq-rj.a.run.app',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'storages',             # ← ADICIONE ESSA (se não tiver)
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.empresa_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database: PostgreSQL em produção, SQLite local
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = False   # mantém ponto como decimal (pt-br usaria vírgula e quebraria inputs)
USE_TZ = True

DECIMAL_SEPARATOR = '.'
USE_THOUSAND_SEPARATOR = False
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'

# Static files (WhiteNoise serve em produção)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Google Cloud Storage - 100% Google
USE_GCS = os.environ.get('USE_GCS', 'False') == 'True'

if USE_GCS:
    # Produção: Google Cloud Storage
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud_storage.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud_storage.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', os.environ.get('GCS_BUCKET_NAME', 'primaaxon-media-files'))
    GS_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
    STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
else:
    # Desenvolvimento: Pasta local
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

