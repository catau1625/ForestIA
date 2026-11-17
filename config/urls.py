from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("equipo/", include("apps.team.urls")),
    path("equipo/admin/", admin.site.urls),
    path("admin/", RedirectView.as_view(url="/equipo/admin/", permanent=False)),
    path("api/v1/", include("config.api_urls")),
]
