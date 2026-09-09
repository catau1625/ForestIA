from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ParcelViewSet, SoilProfileViewSet

router = DefaultRouter()
router.register("parcels", ParcelViewSet, basename="parcels")
router.register("profiles", SoilProfileViewSet, basename="soil-profiles")

urlpatterns = [path("", include(router.urls))]
