from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("parcel", "level", "message", "created_at", "acknowledged")
    list_filter = ("level", "acknowledged", "parcel")
    actions = ["acknowledge"]

    @admin.action(description="Marcar como reconocidas")
    def acknowledge(self, request, queryset):
        queryset.update(acknowledged=True)
