from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("equipo/", include("apps.team.urls")),
    # El admin se sirve en ambas rutas: la clásica /admin/ y /equipo/admin/.
    path("admin/", admin.site.urls),
    path("equipo/admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]
