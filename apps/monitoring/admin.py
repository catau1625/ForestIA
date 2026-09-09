from django.contrib import admin

from .models import DroneFlight, Sensor, SensorReading


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("code", "parcel", "sensor_type", "depth_cm", "protocol", "is_active")
    list_filter = ("sensor_type", "protocol", "is_active")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("sensor", "timestamp", "moisture_pct", "temperature_c", "ec_ds_m")
    list_filter = ("sensor",)


@admin.register(DroneFlight)
class DroneFlightAdmin(admin.ModelAdmin):
    list_display = ("parcel", "flown_at", "ndvi_mean", "ndre_mean")
