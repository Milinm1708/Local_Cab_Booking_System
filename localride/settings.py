"""
Django settings for the LocalRide project.
A free, open-source local cab booking platform built with
Django + SQLite + Leaflet.js/OpenStreetMap (no paid APIs).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------
SECRET_KEY = 'django-insecure-localride-demo-secret-key-change-in-production-987654321'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # LocalRide apps
    'core',
    'accounts',
    'rides',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'localride.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'localride.wsgi.application'

# ------------------------------------------------------------------
# DATABASE (SQLite - free, file-based, zero config)
# ------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:redirect_after_login'
LOGOUT_REDIRECT_URL = 'core:home'

# ------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------
# EMAIL (console backend - free, no external service, prints to terminal)
# ------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'LocalRide <no-reply@localride.example.com>'

# ------------------------------------------------------------------
# LOCALRIDE APP SETTINGS
# ------------------------------------------------------------------
FARE_BASE = 40.0          # base fare in Rs
FARE_PER_KM = 12.0        # per km rate in Rs
FARE_PER_MIN = 1.5        # per minute rate in Rs
FARE_MULTIPLIERS = {
    'mini': 1.0,
    'sedan': 1.35,
    'suv': 1.75,
}
