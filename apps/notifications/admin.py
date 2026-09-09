from django.contrib import admin

from .models import NotificationChannel, NotificationLog


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "is_active")
    list_filter = ("type", "is_active")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("alert", "channel", "status", "created_at", "detail")
    list_filter = ("status", "channel")
