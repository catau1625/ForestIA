"""Intranet de equipo ForestIA: calendario compartido, actividad, tareas,
archivos y sala de reuniones. Solo personal con acceso al staff (is_staff)."""
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Event(models.Model):
    """Evento del calendario compartido (único para todo el equipo)."""

    title = models.CharField("título", max_length=200)
    start = models.DateTimeField("inicio")
    end = models.DateTimeField("fin", null=True, blank=True)
    all_day = models.BooleanField("todo el día", default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="team_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]
        verbose_name = "evento"

    def __str__(self):
        return self.title


class Activity(models.Model):
    """Registro de actividad del equipo (agregó / actualizó / eliminó)."""

    ADD, CHANGE, DELETE = "add", "change", "delete"
    ACTION_CHOICES = [
        (ADD, "agregó"),
        (CHANGE, "actualizó"),
        (DELETE, "eliminó"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    target = models.CharField(max_length=220, help_text="Descripción del objeto afectado")
    url = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "actividad"
        verbose_name_plural = "actividad"

    def __str__(self):
        user = self.user.get_username() if self.user else "alguien"
        return f"{user} {self.get_action_display()} {self.target}"

    @staticmethod
    def log(user, action, target, url=""):
        act = Activity.objects.create(user=user, action=action, target=target[:220], url=url[:300])
        Activity._notify(act)
        return act

    @staticmethod
    def _notify(act):
        """Encola el aviso por correo al resto del equipo (nunca rompe la vista)."""
        import logging

        logger = logging.getLogger(__name__)
        try:
            from apps.team.tasks import notify_team_activity

            notify_team_activity.delay(act.pk)
        except Exception:  # noqa: BLE001
            logger.exception("No se pudo encolar la notificación de la actividad %s", act.pk)


class TaskList(models.Model):
    """Columna del tablero tipo Trello."""

    name = models.CharField("nombre", max_length=80)
    order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "lista de tareas"

    def __str__(self):
        return self.name


class Task(models.Model):
    """Tarjeta del tablero. Sin asignada = la puede tomar cualquiera."""

    task_list = models.ForeignKey(
        TaskList, on_delete=models.CASCADE, related_name="tasks", verbose_name="lista"
    )
    title = models.CharField("título", max_length=200)
    note = models.TextField("nota", blank=True)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="asignada a",
        help_text="Vacío = la puede hacer cualquiera",
    )
    due = models.DateField("vence", null=True, blank=True)
    order = models.PositiveIntegerField("orden", default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "tarea"

    def __str__(self):
        return self.title


def team_upload_path(instance, filename):
    import os
    from django.utils import timezone

    stamp = timezone.now().strftime("%Y%m/%d")
    return os.path.join("team", stamp, filename)


class Folder(models.Model):
    """Carpeta de la nube de archivos (árbol simple)."""

    name = models.CharField("nombre", max_length=120)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_folders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "carpeta"

    def __str__(self):
        return self.name

    def path_names(self):
        chain, node = [], self
        while node:
            chain.append(node.name)
            node = node.parent
        return " / ".join(reversed(chain))


class SharedFile(models.Model):
    """Archivo subido a la nube del equipo."""

    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, null=True, blank=True, related_name="files"
    )
    file = models.FileField("archivo", upload_to=team_upload_path)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="uploaded_files"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "archivo compartido"

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        import os

        return os.path.basename(self.file.name)

    @property
    def size_kb(self):
        try:
            return self.file.size // 1024
        except Exception:
            return 0
