"""Configuración de Django para ForestIA."""
import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-cambiar-en-produccion")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # terceros
    "rest_framework",
    "django_filters",
    # apps de ForestIA
    "apps.dashboard",
    "apps.crops",
    "apps.soils",
    "apps.monitoring",
    "apps.weather",
    "apps.simulation",
    "apps.alerts",
    "apps.notifications",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            # Loader sin caché: en desarrollo los cambios de plantilla se ven
            # al instante incluso con runserver --noreload.
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    # Sin DB_NAME → SQLite (desarrollo). Con DB_NAME → PostgreSQL.
    # En Docker Compose la base usa la imagen postgis/postgis; para geometrías
    # migrar el ENGINE a django.contrib.gis.db.backends.postgis.
    "default": (
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER", default="forestia"),
            "PASSWORD": config("DB_PASSWORD", default="forestia"),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "PORT": config("DB_PORT", default="5432"),
        }
        if config("DB_NAME", default="")
        else {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

# Celery
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_TIMEZONE = TIME_ZONE

# Notificaciones (WhatsApp u otros canales). Ver apps/notifications/dispatchers.py.
WHATSAPP_TOKEN = config("WHATSAPP_TOKEN", default="")
WHATSAPP_API_URL = config("WHATSAPP_API_URL", default="https://graph.facebook.com/v21.0")

# Tareas periódicas (requiere `celery -A config beat`)
from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    # Pronóstico agro fresco cada 6 horas (minuto 17, fuera de hora pico)
    "sync-weather-6h": {
        "task": "apps.weather.tasks.sync_weather_all",
        "schedule": crontab(minute=17, hour="*/6"),
        "kwargs": {"days": 3},
    },
    # Re-simulación diaria de las parcelas activas (05:23, antes del día de campo)
    "resimulate-daily": {
        "task": "apps.simulation.tasks.resimulate_parcels",
        "schedule": crontab(minute=23, hour=5),
    },
}
