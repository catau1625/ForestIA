"""Canales de notificación y registro de envíos (WhatsApp, Telegram, email...)."""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
