"""Sensores de campo, lecturas y vuelos de drone multiespectral."""
from django.db import models
from django.utils import timezone

from apps.soils.models import Parcel


class Sensor(models.Model):
    """Sonda instalada en una parcela (capacitiva, tensiómetro, CE...)."""

    class SensorType(models.TextChoices):
        CAPACITIVO = "capacitivo", "Humedad capacitiva"
        TENSIOMETRO = "tensiometro", "Tensiómetro"
        CONDUCTIVIDAD = "conductividad", "Conductividad eléctrica"
        CLIMA = "clima", "Estación meteorológica"

    class Protocol(models.TextChoices):
        LORA = "lora", "LoRaWAN"
        MQTT = "mqtt", "MQTT"
        API = "api", "API directa"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="sensors")
    code = models.CharField("código", max_length=40, unique=True)  # ej. S1-15CM
    sensor_type = models.CharField("tipo", max_length=20, choices=SensorType.choices)
    depth_cm = models.PositiveIntegerField("profundidad (cm)", null=True, blank=True)
    protocol = models.CharField("protocolo", max_length=10, choices=Protocol.choices, default=Protocol.LORA)
    installed_at = models.DateField("instalado el", default=timezone.localdate)
    is_active = models.BooleanField("activo", default=True)

    class Meta:
        ordering = ["parcel", "depth_cm"]

    def __str__(self):
        return self.code


class SensorReading(models.Model):
    """Lectura telemétrica de una sonda."""

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="readings")
    timestamp = models.DateTimeField("fecha y hora")
    moisture_pct = models.FloatField("humedad (%)", null=True, blank=True)
    temperature_c = models.FloatField("temperatura (°C)", null=True, blank=True)
    ec_ds_m = models.FloatField("conductividad (dS/m)", null=True, blank=True)
    battery_pct = models.FloatField("batería (%)", null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["sensor", "timestamp"])]

    def __str__(self):
        return f"{self.sensor.code} @ {self.timestamp:%Y-%m-%d %H:%M}"


class DroneFlight(models.Model):
    """Vuelo multiespectral con índices de vegetación por parcela."""

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="drone_flights")
    flown_at = models.DateTimeField("fecha del vuelo")
    ndvi_mean = models.FloatField("NDVI medio", null=True, blank=True)
    ndre_mean = models.FloatField("NDRE medio", null=True, blank=True)
    gndvi_mean = models.FloatField("GNDVI medio", null=True, blank=True)
    orthomosaic = models.FileField("ortomosaico", upload_to="drones/", null=True, blank=True)
    zoning_map = models.FileField("mapa de zonas de manejo", upload_to="drones/", null=True, blank=True)

    class Meta:
        ordering = ["-flown_at"]

    def __str__(self):
        return f"{self.parcel} · vuelo {self.flown_at:%Y-%m-%d}"
