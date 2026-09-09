from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SimulationRunViewSet

router = DefaultRouter()
router.register("runs", SimulationRunViewSet, basename="simulation-runs")

urlpatterns = [path("", include(router.urls))]
