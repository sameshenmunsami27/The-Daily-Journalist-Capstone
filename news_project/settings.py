"""
Django settings for news_project.
This module contains the core configuration for the application, including
database connections, authentication backends, REST framework settings,
and email server configurations.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (
    "django-insecure-=(irsjgmurz1fcp2dez3)"
    "+h1jjf=9-=habfb=metpa(yl8#@hm"
)
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",  # Added for REST API
    "rest_framework.authtoken",  # Added for Token Authentication
    "news.apps.NewsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "news_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Flat templates folder logic
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "news_project.wsgi.application"

# DATABASE CONFIGURATION (No Password)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_db",
        "USER": "root",
        "PASSWORD": "",
        "HOST": "host.docker.internal",  # Updated for Docker for connectivity
        "PORT": "3306",
        "OPTIONS": {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation."
     "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation."
     "NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#  CUSTOM PROJECT SETTINGS
"""
Project-specific overrides and third-party library configurations.
"""
AUTH_USER_MODEL = "news.User"

#  REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# AUTHENTICATION REDIRECTS
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

# EMAIL CONFIGURATION (GMAIL)
"""
SMTP settings for outgoing article notifications and password resets.
"""
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "sameshenmunsami27@gmail.com"
EMAIL_HOST_PASSWORD = "bhmkoeolypavltux"
DEFAULT_FROM_EMAIL = "The Daily Journalist <sameshenmunsami27@gmail.com>"

# SECURITY
# Password reset link expires after 3 hours (10800 seconds)
PASSWORD_RESET_TIMEOUT = 10800

LOGOUT_ON_GET = True

# Registration settings
ACCOUNT_ADAPTER = 'django.contrib.auth.models.User'
# If you want users to stay as 'READER' by default
DEFAULT_USER_ROLE = 'READER'
