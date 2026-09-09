"""Registro climático agro de cada parcela (pronóstico y serie histórica)."""
from django.db import models

from apps.soils.models import Parcel


class WeatherRecord(models.Model):
    """Lectura climática agregada (diaria u horaria)."""

    class Source(models.TextChoices):
        OPEN_METEO = "open_meteo", "Open-Meteo"
        OPENWEATHER = "openweather", "OpenWeather"
        ESTACION = "estacion", "Estación propia"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="weather_records")
    timestamp = models.DateTimeField("fecha y hora")
    temp_c = models.FloatField("temperatura (°C)", null=True, blank=True)
    humidity_pct = models.FloatField("humedad relativa (%)", null=True, blank=True)
    wind_ms = models.FloatField("viento (m/s)", null=True, blank=True)
    rain_mm = models.FloatField("lluvia (mm)", null=True, blank=True)
    solar_radiation_mj = models.FloatField("radiación solar (MJ/m²)", null=True, blank=True)
    et0_mm = models.FloatField("evapotranspiración de referencia ET0 (mm)", null=True, blank=True)
    source = models.CharField("fuente", max_length=15, choices=Source.choices, default=Source.OPEN_METEO)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["parcel", "timestamp"])]

    def __str__(self):
        return f"{self.parcel} · {self.timestamp:%Y-%m-%d %H:%M}"
