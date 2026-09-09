"""Ejecuciones de simulación predictiva por parcela y cultivo."""
from django.db import models

from apps.crops.models import Plant
from apps.soils.models import Parcel, SoilProfile


class SimulationRun(models.Model):
    """Una corrida del modelo predictivo."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En ejecución"
        DONE = "done", "Completada"
        FAILED = "failed", "Fallida"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="simulations")
    plant = models.ForeignKey(Plant, on_delete=models.PROTECT, related_name="simulations")
    soil_profile = models.ForeignKey(
        SoilProfile, on_delete=models.PROTECT, related_name="simulations", null=True, blank=True
    )
    horizon_days = models.PositiveIntegerField("horizonte (días)", default=180)
    initial_moisture_pct = models.FloatField("humedad inicial (%)", default=35)
    initial_nitrogen_ppm = models.FloatField("N inicial (ppm)", default=70)
    status = models.CharField("estado", max_length=10, choices=Status.choices, default=Status.PENDING)
    result = models.JSONField("resultado", null=True, blank=True)
    created_at = models.DateTimeField("creada el", auto_now_add=True)
    finished_at = models.DateTimeField("finalizada el", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.parcel} · {self.plant} · {self.created_at:%Y-%m-%d %H:%M}"
