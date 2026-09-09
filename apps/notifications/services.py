"""Envío de alertas por los canales activos."""
import logging

from apps.alerts.models import Alert

from .dispatchers import DISPATCHERS
from .models import NotificationChannel, NotificationLog

logger = logging.getLogger(__name__)


def send_alert(alert: Alert) -> list[NotificationLog]:
    """Despacha una alerta por todos los canales activos y registra el resultado.

    Nunca lanza excepciones: un canal caído no debe romper la generación
    de alertas. Los envíos quedan en NotificationLog con estado
    sent / pending / failed para auditoría y reintentos.
    """
    logs = []
    for channel in NotificationChannel.objects.filter(is_active=True):
        try:
            dispatcher = DISPATCHERS[channel.type]
            result = dispatcher.send(alert, channel)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Canal %s falló al enviar la alerta %s", channel, alert.pk)
            result_status, result_ok, detail = "failed", False, str(exc)
        else:
            result_status, result_ok, detail = result.status, result.ok, result.detail
        logs.append(
            NotificationLog.objects.create(
                alert=alert,
                channel=channel,
                status=result_status,
                detail=detail,
            )
        )
    return logs
