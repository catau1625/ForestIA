from django.urls import path

from .views import dashboard, launch_simulation

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("simular/", launch_simulation, name="launch-simulation"),
]
