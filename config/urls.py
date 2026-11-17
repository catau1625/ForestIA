from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path


def admin_legacy_redirect(request, rest=""):
    """/equipo/admin/ queda inutilizada: redirige a la ruta canónica /admin/."""
    return redirect(f"/admin/{rest}")


urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("equipo/", include("apps.team.urls")),
    path("admin/", admin.site.urls),
    re_path(r"^equipo/admin/(?P<rest>.*)$", admin_legacy_redirect),
    path("api/v1/", include("config.api_urls")),
]
