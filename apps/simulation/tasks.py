from django.utils import timezone
from django.db.models import Avg, Sum
from django.db.models.functions import TruncDate

from apps.alerts.models import Alert
from apps.crops.models import Plant
from apps.weather.models import WeatherRecord
from config.celery import app

from .engine import run_simulation
from .models import SimulationRun


def _weather_forecast_for(parcel, horizon_days: int) -> list[dict]:
    """Agrega el pronóstico Open-Meteo guardado en registros diarios (día 0..N)."""
    qs = (
        WeatherRecord.objects.filter(
            parcel=parcel,
            timestamp__gte=timezone.now(),
        )
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(et0_mm=Avg("et0_mm"), rain_mm=Sum("rain_mm"))
        .order_by("day")
    )
    by_day = {}
    for row in qs:
        day_index = (row["day"] - timezone.localdate()).days
        if 0 <= day_index <= horizon_days:
            by_day[day_index] = {
                "et0_mm": row["et0_mm"] or 0.0,
                "rain_mm": row["rain_mm"] or 0.0,
            }
    return [by_day.get(d, {}) for d in range(horizon_days + 1)]


@app.task(bind=True, max_retries=2)
def run_simulation_task(self, run_id: int):
    """Ejecuta el modelo con clima real y genera alertas a partir de los resultados."""
    run = SimulationRun.objects.select_related("plant", "parcel", "soil_profile").get(pk=run_id)
    run.status = SimulationRun.Status.RUNNING
    run.save(update_fields=["status"])
    try:
        plant: Plant = run.plant
        soil_type = run.soil_profile.soil_type if run.soil_profile else "franco"
        n_demand_cycle = sum(s.nitrogen_ppm for s in plant.stages.all()) or plant.kc_mid * 80
        result = run_simulation(
            cycle_days=plant.cycle_days,
            growth_rate=plant.growth_rate,
            t_mid=plant.cycle_days // 2,
            nitrogen_demand_cycle_ppm=n_demand_cycle,
            kc_initial=plant.kc_initial,
            kc_mid=plant.kc_mid,
            kc_end=plant.kc_end,
            soil_type=soil_type,
            initial_moisture_pct=run.initial_moisture_pct,
            initial_nitrogen_ppm=run.initial_nitrogen_ppm,
            horizon_days=run.horizon_days,
            weather_daily=_weather_forecast_for(run.parcel, run.horizon_days),
        )
        run.result = result
        run.status = SimulationRun.Status.DONE
        run.finished_at = timezone.now()
        run.save(update_fields=["result", "status", "finished_at"])
        _generate_alerts(run)
    except Exception as exc:  # noqa: BLE001
        run.status = SimulationRun.Status.FAILED
        run.save(update_fields=["status"])
        raise self.retry(exc=exc, countdown=10)


@app.task(bind=True, max_retries=2)
def resimulate_parcels(self):
    """Re-ejecuta la última simulación completada de cada parcela.

    Corre una vez al día vía Celery Beat: mantiene las predicciones
    alineadas con el pronóstico climático más reciente.
    """
    from apps.soils.models import Parcel

    for parcel in Parcel.objects.all():
        last = parcel.simulations.filter(status="done").first()
        if not last:
            continue
        run = SimulationRun.objects.create(
            parcel=parcel,
            plant=last.plant,
            soil_profile=last.soil_profile,
            horizon_days=last.horizon_days,
            initial_moisture_pct=last.initial_moisture_pct,
            initial_nitrogen_ppm=last.initial_nitrogen_ppm,
        )
        run_simulation_task.apply(args=[run.id])


def _generate_alerts(run: SimulationRun):
    final = run.result["final"]
    created = []
    if final["moisture_pct"] < 18:
        created.append(
            Alert.objects.create(
                parcel=run.parcel,
                level=Alert.Level.WARNING,
                message=f"Riego recomendado: humedad proyectada a {final['moisture_pct']} % "
                f"en {run.horizon_days} días.",
            )
        )
    if final["nitrogen_ppm"] < 28:
        created.append(
            Alert.objects.create(
                parcel=run.parcel,
                level=Alert.Level.DANGER,
                message=f"Planificar fertirrigación: N proyectado a {final['nitrogen_ppm']} ppm.",
            )
        )
    # Notificar por los canales configurados (WhatsApp, etc.). Nunca rompe la tarea.
    from apps.notifications.services import send_alert

    for alert in created:
        try:
            send_alert(alert)
        except Exception:  # noqa: BLE001
            pass
