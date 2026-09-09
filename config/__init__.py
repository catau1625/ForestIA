"""Permite usar `celery -A config` sin un módulo extra."""
from .celery import app as celery_app

__all__ = ("celery_app",)
