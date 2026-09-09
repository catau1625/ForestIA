from django.contrib import admin

from .models import WeatherRecord


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("parcel", "timestamp", "temp_c", "humidity_pct", "rain_mm", "et0_mm", "source")
    list_filter = ("source", "parcel")
