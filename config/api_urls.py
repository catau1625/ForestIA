from django.urls import include, path

urlpatterns = [
    path("crops/", include("apps.crops.urls")),
    path("soils/", include("apps.soils.urls")),
    path("monitoring/", include("apps.monitoring.urls")),
    path("weather/", include("apps.weather.urls")),
    path("simulation/", include("apps.simulation.urls")),
    path("alerts/", include("apps.alerts.urls")),
]
