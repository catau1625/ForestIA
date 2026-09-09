from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PlantViewSet

router = DefaultRouter()
router.register("plants", PlantViewSet, basename="plants")

urlpatterns = [path("", include(router.urls))]
