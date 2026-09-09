"""Sincroniza el pronóstico agro de Open-Meteo para las parcelas georreferenciadas.

Uso:
    python manage.py sync_weather                # todas las parcelas, 7 días
    python manage.py sync_weather --days 14      # horizonte extendido
    python manage.py sync_weather --parcel 1     # una parcela puntual
"""
from django.core.management.base import BaseCommand, CommandError

from apps.soils.models import Parcel
from apps.weather.integrations.openmeteo import fetch_agro_weather
from apps.weather.models import WeatherRecord


class Command(BaseCommand):
    help = "Descarga pronóstico agro (ET0, lluvia, radiación) de Open-Meteo y lo guarda por parcela."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Días de pronóstico (máx. 16).")
        parser.add_argument("--parcel", type=int, default=None, help="ID de parcela puntual.")

    def handle(self, *args, **options):
        days = min(options["days"], 16)
        parcels = Parcel.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        if options["parcel"]:
            parcels = parcels.filter(pk=options["parcel"])

        if not parcels.exists():
            raise CommandError(
                "No hay parcelas georreferenciadas. Asigná latitud y longitud en el admin."
            )

        total = 0
        for parcel in parcels:
            try:
                records = fetch_agro_weather(parcel.latitude, parcel.longitude, days=days)
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f"{parcel}: falló la descarga ({exc})"))
                continue
            for rec in records:
                WeatherRecord.objects.update_or_create(
                    parcel=parcel,
                    timestamp=rec["timestamp"],
                    source=WeatherRecord.Source.OPEN_METEO,
                    defaults=rec,
                )
                total += 1
            self.stdout.write(
                self.style.SUCCESS(f"{parcel}: {len(records)} registros horarios ({days} días)")
            )

        self.stdout.write(self.style.SUCCESS(f"Listo. {total} registros sincronizados."))
