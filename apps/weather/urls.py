from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WeatherRecordViewSet

router = DefaultRouter()
router.register("records", WeatherRecordViewSet, basename="weather-records")

urlpatterns = [path("", include(router.urls))]
