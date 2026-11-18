"""Backend de correo vía API HTTP (compatible con Resend y similares).

DigitalOcean bloquea el tráfico SMTP saliente (puertos 25/465/587) por
defecto, por lo que el envío tradicional no funciona desde el droplet.
Este backend envía por HTTPS (puerto 443, que sí está abierto) usando una
API de correo. Para activarlo, en el .env:

    EMAIL_BACKEND=apps.notifications.backends.HttpApiEmailBackend
    EMAIL_API_URL=https://api.resend.com/emails
    EMAIL_API_KEY=re_xxxx...
    DEFAULT_FROM_EMAIL=ForestIA Equipo <hola@tudominio.cl>
"""
import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class HttpApiEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        url = getattr(settings, "EMAIL_API_URL", "")
        key = getattr(settings, "EMAIL_API_KEY", "")
        if not url or not key:
            if self.fail_silently:
                return 0
            raise RuntimeError("EMAIL_API_URL y EMAIL_API_KEY deben estar configurados en el entorno.")

        sent = 0
        for msg in email_messages:
            recipients = list(msg.to or []) + list(msg.cc or []) + list(msg.bcc or [])
            payload = {
                "from": msg.from_email,
                "to": recipients,
                "subject": msg.subject,
                "text": msg.body,
            }
            try:
                resp = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=20,
                )
            except requests.RequestException as exc:
                if not self.fail_silently:
                    raise RuntimeError(f"Error de conexión con la API de correo: {exc}")
                continue
            if resp.status_code in (200, 201, 202, 204):
                sent += 1
            elif not self.fail_silently:
                raise RuntimeError(f"La API de correo respondió {resp.status_code}: {resp.text[:300]}")
        return sent
