"""Configuración de Celery para ForestIA.

Arrancar el worker con:
    celery -A config worker -l info
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("forestia")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
