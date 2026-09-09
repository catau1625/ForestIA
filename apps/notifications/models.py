"""Modelos del sistema de notificaciones."""
from django.db import models

from apps.alerts.models import Alert


class NotificationChannel(models.Model):
    """Canal de envío: WhatsApp, Telegram, email, etc.

    ``config`` guarda parámetros del canal en JSON, por ejemplo
    {"phone": "+549..."} para WhatsApp. Las credenciales globales
    (tokens, API keys) viven en variables de entorno / settings,
    nunca en la base de datos.
    """

    class Type(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Email"

    name = models.CharField("nombre", max_length=80)
    type = models.CharField("tipo", max_length=15, choices=Type.choices)
    config = models.JSONField("configuración", default=dict, blank=True)
    is_active = models.BooleanField("activo", default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class NotificationLog(models.Model):
    """Registro de cada intento de envío de una alerta."""

    class Status(models.TextChoices):
        SENT = "sent", "Enviada"
        PENDING = "pending", "Pendiente (falta configuración)"
        FAILED = "failed", "Fallida"

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="notifications")
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    status = models.CharField("estado", max_length=10, choices=Status.choices)
    detail = models.TextField("detalle", blank=True)
    created_at = models.DateTimeField("creado el", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alert} → {self.channel} [{self.get_status_display()}]"
