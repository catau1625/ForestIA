"""Tareas Celery de la intranet de equipo."""
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_team_activity(self, activity_id: int):
    """Avisa por correo al resto del equipo cuando alguien hace algo.

    Se dispara desde ``Activity.log``; los destinatarios son las usuarias
    activas con acceso de staff que tengan correo, excepto quien hizo la acción.
    """
    from apps.team.models import Activity  # import local: evita ciclo

    try:
        act = Activity.objects.select_related("user").get(pk=activity_id)
    except Activity.DoesNotExist:
        return

    User = get_user_model()
    recipients = list(
        User.objects.filter(is_active=True, is_staff=True)
        .exclude(pk=act.user_id)
        .exclude(email__isnull=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not recipients:
        return

    who = act.user.get_username() if act.user else "alguien"
    action = act.get_action_display()
    subject = f"ForestIA Equipo · {who} {action} {act.target}"
    link = f"{settings.SITE_URL}{act.url}" if act.url else settings.SITE_URL
    body = (
        f"Hola:\n\n{who} {action} {act.target} en la intranet de ForestIA.\n\n"
        f"Ver en la plataforma: {link}\n\n"
        f"— Notificación automática de ForestIA (por favor no responder)"
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception as exc:  # noqa: BLE001
        logger.exception("No se pudo enviar la notificación de actividad %s", activity_id)
        raise self.retry(exc=exc)
