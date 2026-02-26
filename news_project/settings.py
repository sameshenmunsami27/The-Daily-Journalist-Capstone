"""
Django settings for news_project.
This module contains the core configuration for the application, including
database connections, authentication backends, REST framework settings,
and email server configurations.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# Helper function to read from secrets_keys.txt safely
def get_secret(key_name, default=None):
    try:
        with open(os.path.join(BASE_DIR, "secrets_keys.txt"), "r") as f:
            for line in f:
                if "=" in line:
                    name, value = line.split("=", 1)
                    if name.strip() == key_name:
                        return value.strip()
    except FileNotFoundError:
        return default
    return default


# Keep the secret key used in production secret.
# In the fallback_key section below you enter the DJANGO SECRET KEY
fallback_key = "django-insecure-placeholder-key-for-local-dev-only"
SECRET_KEY = get_secret("DJANGO_SECRET_KEY", fallback_key)

DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
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
        "DIRS": [BASE_DIR / "templates"],
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

# DATABASE CONFIGURATION
# Passwords and Users are now pulled from secrets_keys.txt
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_secret("MYSQL_DATABASE", "news_db"),
        "USER": get_secret("MYSQL_USER", "root"),
        "PASSWORD": get_secret("MYSQL_PASSWORD", ""),
        "HOST": os.environ.get("DATABASE_HOST", "127.0.0.1"),
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
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

AUTH_USER_MODEL = "news.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

# EMAIL CONFIGURATION (GMAIL)
# Confidential information removed and delegated to get_secret
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Below is where you enter my email address
EMAIL_HOST_USER = get_secret("EMAIL_USER", "")
# Below is where you enter my email APP password
EMAIL_HOST_PASSWORD = get_secret("EMAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = f"The Daily Journalist <{EMAIL_HOST_USER}>"

# SECURITY
PASSWORD_RESET_TIMEOUT = 10800
LOGOUT_ON_GET = True
DEFAULT_USER_ROLE = "READER"
