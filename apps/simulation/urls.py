from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SimulationRunViewSet, run_preview

router = DefaultRouter()
router.register("runs", SimulationRunViewSet, basename="simulation-runs")

urlpatterns = [
    path("runs/<int:pk>/preview/", run_preview, name="simulation-run-preview"),
    path("", include(router.urls)),
]
