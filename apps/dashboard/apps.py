"""Panel principal de ForestIA: parcelas, sensores, clima, alertas y simulaciones."""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
