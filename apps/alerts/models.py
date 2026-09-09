"""Alertas agronómicas generadas por las simulaciones o por umbrales de sensores."""
from django.db import models

from apps.soils.models import Parcel


class Alert(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "Informativa"
        WARNING = "warning", "Advertencia"
        DANGER = "danger", "Crítica"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="alerts")
    level = models.CharField("nivel", max_length=10, choices=Level.choices, default=Level.INFO)
    message = models.TextField("mensaje")
    created_at = models.DateTimeField("creada el", auto_now_add=True)
    acknowledged = models.BooleanField("reconocida", default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_level_display()}] {self.parcel}"
