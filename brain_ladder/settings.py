import os
import logging
from pathlib import Path
from decouple import config, Csv

# =========================
# Base directory
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# SECURITY
# =========================
SECRET_KEY = config("SECRET_KEY", default="django-insecure-test-key")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# =========================
# Installed apps ok ok
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "game",       # your app
    "storages",   # for Supabase S3 storage
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "brain_ladder.urls"

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

WSGI_APPLICATION = "brain_ladder.wsgi.application"

# =========================
# Database (Supabase Postgres)
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", default=5432, cast=int),
    }
}

# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = []

# =========================
# Internationalization
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =========================
# Static files
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# =========================
# Media / File storage (Supabase S3)
# =========================
# =========================
# Media / File storage (Supabase S3)
# =========================
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
#AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
# Remove or comment this line (not needed for Supabase):
# AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.storage.supabase.co"




# =========================
# Authentication redirects
# =========================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# =========================
# Razorpay keys
# =========================
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID", default="rzp_test_A8YS3sL3hDWZWu")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET", default="ezPN6gzRNAjAybF3ojsgeRIX")

# =========================
# Auto primary key type
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# CSRF Trusted Origins
# =========================
CSRF_TRUSTED_ORIGINS = [
    "https://quiz-ladder.fly.dev",
]

# =========================
# Logging configuration
# =========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "storages": {
            "handlers": ["console"],
            "level": "DEBUG",  # show all S3 storage logs
            "propagate": False,
        },
        "boto3": {
            "handlers": ["console"],
            "level": "DEBUG",  # boto3 SDK logs
            "propagate": False,
        },
        "botocore": {
            "handlers": ["console"],
            "level": "DEBUG",  # low-level AWS/S3 errors
            "propagate": False,
        },
    },
}

AWS_QUERYSTRING_AUTH = False
MEDIA_URL = "https://tbweyeoutumitoggtuhi.supabase.co/storage/v1/object/public/kyc-documents/"
