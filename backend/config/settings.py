"""
Django settings for the DMS (Debt Management System) project.

Key decisions:
  - AUTH_USER_MODEL is set to 'users.User' BEFORE any app that references it,
    because Django resolves the model at startup time. Changing this after the
    first migration would require resetting the entire database.
  - SIMPLE_JWT lifetimes follow the spec: 15-min access, 7-day refresh.
  - CORS is open in development (CORS_ALLOW_ALL_ORIGINS=True); tighten for prod.
"""

import os
from datetime import timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# Read SECRET_KEY from the environment so it is never committed to source control.
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# DEBUG should be True locally and False in any deployed environment.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Comma-separated list of hostnames; split into a Python list at runtime.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",           # Django REST Framework
    "corsheaders",              # Allow the Vite dev server to call the API
    # Local
    "users",                    # Our custom auth app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",   # Must come before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Supports DATABASE_URL env var (e.g. postgres://user:pass@host:port/dbname)
# OR individual DB_* variables.  Falls back to SQLite for quick local dev.
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "dms"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
            "HOST": os.environ.get("DB_HOST", "db"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# ---------------------------------------------------------------------------
# Custom User Model
# ---------------------------------------------------------------------------
# IMPORTANT: This must be set before running any migrations.
# Changing AUTH_USER_MODEL after migrations exist requires wiping the DB.
AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Use JWT Bearer tokens as the default authentication scheme.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # By default, every endpoint requires authentication.
    # Public endpoints override this with AllowAny permission class.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ---------------------------------------------------------------------------
# Simple JWT configuration (spec §1.3)
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Short-lived access token reduces exposure window if a token is leaked.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    # Longer refresh token allows "stay logged in" UX without re-entering credentials.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Do NOT rotate refresh tokens — a single refresh token stays valid for 7 days.
    "ROTATE_REFRESH_TOKENS": False,
    # The Authorization header value must be:  Bearer <token>
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# In development, allow the Vite dev server (port 5173) to call the API.
# In production, replace with the exact frontend origin.
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True locally, must be False in prod
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
