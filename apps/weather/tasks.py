"""Tareas periódicas de clima para Celery Beat."""
from celery import shared_task

from apps.soils.models import Parcel
from apps.weather.integrations.openmeteo import fetch_agro_weather
from apps.weather.models import WeatherRecord


def sync_parcel_weather(parcel: Parcel, days: int = 3) -> int:
    """Baja el pronóstico de Open-Meteo de una parcela y lo guarda (idempotente)."""
    if parcel.latitude is None or parcel.longitude is None:
        return 0
    records = fetch_agro_weather(parcel.latitude, parcel.longitude, days=days)
    for rec in records:
        WeatherRecord.objects.update_or_create(
            parcel=parcel,
            timestamp=rec["timestamp"],
            source=WeatherRecord.Source.OPEN_METEO,
            defaults=rec,
        )
    return len(records)


@shared_task
def sync_weather_all(days: int = 3) -> dict:
    """Sincroniza el pronóstico de todas las parcelas georreferenciadas."""
    result = {}
    for parcel in Parcel.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        result[parcel.name] = sync_parcel_weather(parcel, days=days)
    return result
