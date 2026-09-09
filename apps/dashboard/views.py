"""Vista del panel principal de ForestIA."""
from django.shortcuts import render

from apps.alerts.models import Alert
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
        {"parcels": parcels, "totals": totals},
    )
