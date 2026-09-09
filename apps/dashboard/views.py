"""Vista del panel principal de ForestIA."""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.alerts.models import Alert
from apps.crops.models import Plant
from apps.simulation.models import SimulationRun
from apps.simulation.tasks import run_simulation_task
from apps.soils.models import Parcel


def _parcel_context(parcel: Parcel) -> dict:
    sensors = []
    for sensor in parcel.sensors.filter(is_active=True).prefetch_related("readings"):
        last = sensor.readings.first()
        sensors.append(
            {
                "sensor": sensor,
                "last": last,
            }
        )
    latest_alert = parcel.alerts.first()
    latest_run = parcel.simulations.filter(status="done").first()
    latest_flight = parcel.drone_flights.first()
    latest_weather = parcel.weather_records.first()
    open_alerts = parcel.alerts.filter(acknowledged=False).count()
    return {
        "parcel": parcel,
        "sensors": sensors,
        "latest_alert": latest_alert,
        "open_alerts": open_alerts,
        "latest_run": latest_run,
        "latest_flight": latest_flight,
        "latest_weather": latest_weather,
    }


def dashboard(request):
    parcels = [
        _parcel_context(p)
        for p in Parcel.objects.prefetch_related(
            "sensors", "alerts", "simulations", "drone_flights", "weather_records"
        )
    ]
    totals = {
        "parcels": len(parcels),
        "open_alerts": Alert.objects.filter(acknowledged=False).count(),
        "critical_alerts": Alert.objects.filter(
            acknowledged=False, level=Alert.Level.DANGER
        ).count(),
        "active_sensors": sum(len(p["sensors"]) for p in parcels),
    }
    return render(
        request,
        "dashboard/index.html",
        {
            "parcels": parcels,
            "totals": totals,
            "plants": Plant.objects.all(),
            "all_parcels": Parcel.objects.all(),
        },
    )


MONTHS_TO_DAYS = {"3": 90, "6": 180, "12": 365}


@require_POST
def launch_simulation(request):
    """Crea y ejecuta una simulación desde el formulario del panel.

    Intenta encolarla en Celery; si el broker no está disponible
    (entorno de desarrollo sin Redis), la ejecuta en el momento.
    """
    parcel = Parcel.objects.get(pk=request.POST["parcel"])
    plant = Plant.objects.get(pk=request.POST["plant"])
    run = SimulationRun.objects.create(
        parcel=parcel,
        plant=plant,
        soil_profile=parcel.soil_profiles.first(),
        horizon_days=MONTHS_TO_DAYS.get(request.POST.get("months", "6"), 180),
        initial_moisture_pct=float(request.POST.get("moisture", 35)),
        initial_nitrogen_ppm=float(request.POST.get("nitrogen", 70)),
    )
    try:
        run_simulation_task.delay(run.id)
        messages.success(request, f"Simulación de {plant} encolada (Celery).")
    except Exception:  # noqa: BLE001 — broker caído: ejecutar en línea
        run_simulation_task.apply(args=[run.id])
        messages.success(request, f"Simulación de {plant} completada.")
    return redirect("simulation-run-preview", pk=run.id)
