"""Despachadores de notificación.

Cada canal implementa ``send(alert, channel) -> DispatchResult``. Para
integrar WhatsApp de verdad, completar ``WhatsAppDispatcher.send()`` con la
API elegida (p. ej. WhatsApp Business Cloud API de Meta, Twilio o
CallMeBot) leyendo el token de ``settings.WHATSAPP_TOKEN``. Hasta entonces,
el despachador deja el envío como PENDIENTE con instrucciones claras.
"""
from dataclasses import dataclass

from django.conf import settings

from .models import NotificationChannel


@dataclass
class DispatchResult:
    ok: bool
    status: str  # "sent" | "pending" | "failed"
    detail: str = ""


class BaseDispatcher:
    type_code: str = ""

    def send(self, alert, channel: NotificationChannel) -> DispatchResult:  # pragma: no cover
        raise NotImplementedError


class WhatsAppDispatcher(BaseDispatcher):
    """Listo para integrar: falta conectar la API de mensajería.

    Requiere en settings/entorno:
        WHATSAPP_TOKEN   → token de la API (Meta Cloud API, Twilio, etc.)
        WHATSAPP_API_URL → endpoint de envío (opcional, según proveedor)
    y en ``channel.config``:
        {"phone": "+54911..."}  → destinatario (o grupo)
    """

    type_code = NotificationChannel.Type.WHATSAPP

    def send(self, alert, channel: NotificationChannel) -> DispatchResult:
        token = getattr(settings, "WHATSAPP_TOKEN", "")
        phone = channel.config.get("phone", "")
        if not token or not phone:
            return DispatchResult(
                ok=False,
                status="pending",
                detail=(
                    "WhatsApp aún no configurado: definí WHATSAPP_TOKEN en el entorno "
                    "y {'phone': '+549...'} en la configuración del canal."
                ),
            )
        # TODO(integración): enviar el mensaje a través del proveedor elegido.
        #   message = f"🌱 ForestIA · {alert.get_level_display()}\n{alert.message}"
        #   requests.post(..., headers={"Authorization": f"Bearer {token}"}, json={...})
        #   Verificar la respuesta y devolver DispatchResult(ok=True, status="sent")
        return DispatchResult(
            ok=False,
            status="pending",
            detail="WHATSAPP_TOKEN definido pero la llamada a la API no está implementada todavía.",
        )


class TelegramDispatcher(BaseDispatcher):
    type_code = NotificationChannel.Type.TELEGRAM

    def send(self, alert, channel: NotificationChannel) -> DispatchResult:
        return DispatchResult(ok=False, status="pending", detail="Canal Telegram no implementado.")


class EmailDispatcher(BaseDispatcher):
    """Envío de alertas por correo vía SMTP (settings.EMAIL_*).

    En ``channel.config`` puede definirse:
        {"to": "correo@dominio.cl"}
    o varios destinatarios:
        {"recipients": ["a@x.cl", "b@x.cl"]}
    """

    type_code = NotificationChannel.Type.EMAIL

    def send(self, alert, channel: NotificationChannel) -> DispatchResult:
        from django.core.mail import send_mail

        cfg = channel.config or {}
        recipients = cfg.get("recipients") or ([cfg["to"]] if cfg.get("to") else [])
        if not recipients:
            return DispatchResult(
                ok=False,
                status="pending",
                detail="Canal email sin destinatarios: configurar {'to': 'correo@...'} "
                "o {'recipients': [...]} en el canal.",
            )
        subject = f"ForestIA · {alert.get_level_display()} en {alert.parcel}"
        body = (
            f"{alert.message}\n\n"
            f"Parcela: {alert.parcel}\n"
            f"Nivel: {alert.get_level_display()}\n"
            f"Fecha: {alert.created_at:%d/%m/%Y %H:%M}\n\n"
            f"— Alerta automática de ForestIA"
        )
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        except Exception as exc:  # noqa: BLE001
            return DispatchResult(ok=False, status="failed", detail=str(exc))
        return DispatchResult(ok=True, status="sent", detail=f"Enviado a {len(recipients)} destinatario(s).")


DISPATCHERS = {d.type_code: d for d in (WhatsAppDispatcher(), TelegramDispatcher(), EmailDispatcher())}
