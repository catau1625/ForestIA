from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DroneFlightViewSet, SensorReadingViewSet, SensorViewSet

router = DefaultRouter()
router.register("sensors", SensorViewSet, basename="sensors")
router.register("readings", SensorReadingViewSet, basename="readings")
router.register("flights", DroneFlightViewSet, basename="flights")

urlpatterns = [path("", include(router.urls))]
