"""
Django settings for backend project.
"""

from pathlib import Path
import os
from mongoengine import connect

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# SECURITY
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "*",
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

# Needed for reverse proxy setups (Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# -------------------------------------------------------------------
# STATIC & MEDIA
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -------------------------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",
    "api",
]

# -------------------------------------------------------------------
# MIDDLEWARE (CORS MUST BE FIRST)
# -------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # Whitenoise for static files on Render
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Whitenoise static compression
WHITENOISE_USE_FINDERS = True

# -------------------------------------------------------------------
# URL + TEMPLATES
# -------------------------------------------------------------------
ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# -------------------------------------------------------------------
# DATABASE (SQLite used only for Django auth/session)
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------------------
# MongoDB Atlas Connection
# -------------------------------------------------------------------
connect(
    db="college_app",
    host=os.getenv(
        "MONGODB_URI",
        "mongodb+srv://technicalteam0004:Radhe%405671@cluster0.sj5adex.mongodb.net/college_app?retryWrites=true&w=majority"
    )
)

# -------------------------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}

# -------------------------------------------------------------------
# CORS (FINAL FIXED VERSION — DO NOT CHANGE)
# -------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True   # Fixes 90% of Render/React issues
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "dnt",
    "cache-control",
    "x-requested-with",
]

CORS_EXPOSE_HEADERS = ["Content-Type"]

# -------------------------------------------------------------------
# COOKIES / CSRF (Safe for API-based apps)
# -------------------------------------------------------------------
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = False

# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# LANGUAGE & TIMEZONE
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  

# -------------------------------------------------------------------
# CACHE FOR OTP
# -------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "otp-cache"
    }
}

# -------------------------------------------------------------------
# EMAIL CONFIG (Gmail SMTP)
# -------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "technical.team0004@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "ueqk gmve casx enuq")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

