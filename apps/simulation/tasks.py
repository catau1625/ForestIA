from django.utils import timezone

from apps.alerts.models import Alert
from apps.crops.models import Plant
from config.celery import app

from .engine import run_simulation
from .models import SimulationRun


@app.task(bind=True, max_retries=2)
def run_simulation_task(self, run_id: int):
    """Ejecuta el modelo y genera alertas a partir de los resultados."""
    run = SimulationRun.objects.select_related("plant", "parcel", "soil_profile").get(pk=run_id)
    run.status = SimulationRun.Status.RUNNING
    run.save(update_fields=["status"])
    try:
        plant: Plant = run.plant
        soil_type = run.soil_profile.soil_type if run.soil_profile else "franco"
        result = run_simulation(
            cycle_days=plant.cycle_days,
            growth_rate=plant.growth_rate,
            t_mid=plant.cycle_days // 2,
            nitrogen_demand=max(0.2, plant.kc_mid * 0.8),
            soil_type=soil_type,
            initial_moisture_pct=run.initial_moisture_pct,
            initial_nitrogen_ppm=run.initial_nitrogen_ppm,
            horizon_days=run.horizon_days,
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


def _generate_alerts(run: SimulationRun):
    final = run.result["final"]
    if final["moisture_pct"] < 18:
        Alert.objects.create(
            parcel=run.parcel,
            level=Alert.Level.WARNING,
            message=f"Riego recomendado: humedad proyectada a {final['moisture_pct']} % "
            f"en {run.horizon_days} días.",
        )
    if final["nitrogen_ppm"] < 28:
        Alert.objects.create(
            parcel=run.parcel,
            level=Alert.Level.DANGER,
            message=f"Planificar fertirrigación: N proyectado a {final['nitrogen_ppm']} ppm.",
        )
