"""Vistas de la intranet de equipo (requieren is_staff)."""
import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.alerts.models import Alert
from apps.crops.models import Plant
from apps.monitoring.models import DroneFlight, Sensor, SensorReading
from apps.simulation.models import SimulationRun
from apps.soils.models import Parcel, SoilProfile
from apps.weather.models import WeatherRecord

from .models import Activity, Event, Folder, SharedFile, Task, TaskList

User = get_user_model()


def _log(request, action, target, url=""):
    Activity.log(request.user, action, target, url)


@staff_member_required
def home(request):
    """Hub de la intranet: dos secciones en bloques — Plataforma y Proyecto."""
    today = timezone.localdate()
    now = timezone.now()

    last_reading = SensorReading.objects.select_related("sensor").order_by("-timestamp").first()
    last_weather = WeatherRecord.objects.select_related("parcel").order_by("-timestamp").first()
    last_flight = DroneFlight.objects.select_related("parcel").order_by("-flown_at").first()
    open_danger = Alert.objects.filter(acknowledged=False, level=Alert.Level.DANGER).count()
    open_warn = Alert.objects.filter(acknowledged=False, level=Alert.Level.WARNING).count()
    open_info = Alert.objects.filter(acknowledged=False, level=Alert.Level.INFO).count()

    task_lists = TaskList.objects.prefetch_related("tasks")
    my_tasks = Task.objects.filter(assignee=request.user).select_related("task_list")
    upcoming = Event.objects.filter(start__gte=now).select_related("created_by")[:3]
    recent_files = SharedFile.objects.select_related("uploaded_by").order_by("-id")[:3]

    platform = {
        "parcels": Parcel.objects.count(),
        "profiles": SoilProfile.objects.count(),
        "sensors_active": Sensor.objects.filter(is_active=True).count(),
        "sensors_total": Sensor.objects.count(),
        "last_reading": last_reading,
        "weather_parcels": WeatherRecord.objects.order_by("parcel").values("parcel").distinct().count(),
        "last_weather": last_weather,
        "flights": DroneFlight.objects.count(),
        "last_flight": last_flight,
        "plants": Plant.objects.count(),
        "simulations": SimulationRun.objects.count(),
        "open_alerts": open_danger + open_warn + open_info,
        "open_danger": open_danger,
        "open_warn": open_warn,
    }
    project = {
        "task_lists": task_lists,
        "tasks_total": Task.objects.count(),
        "my_tasks": my_tasks,
        "my_tasks_count": my_tasks.count(),
        "upcoming": upcoming,
        "files_total": SharedFile.objects.count(),
        "folders_total": Folder.objects.count(),
        "recent_files": recent_files,
    }
    return render(
        request,
        "team/home.html",
        {"platform": platform, "project": project, "today": today},
    )


@staff_member_required
def calendar(request):
    today = timezone.localdate()
    upcoming = Event.objects.filter(start__gte=timezone.now()).select_related("created_by")[:10]
    return render(
        request,
        "team/calendar.html",
        {"upcoming": upcoming, "today": today},
    )


@staff_member_required
@require_POST
def event_create(request):
    title = request.POST.get("title", "").strip()
    day = request.POST.get("day", "")
    time_ = request.POST.get("time", "")
    if title and day:
        start_str = f"{day}T{time_ or '09:00'}"
        try:
            start = timezone.datetime.fromisoformat(start_str)
        except ValueError:
            start = None
        if start:
            ev = Event.objects.create(
                title=title, start=start, all_day=not bool(time_), created_by=request.user
            )
            _log(request, Activity.ADD, f"el evento «{ev.title}»", reverse("team-calendar"))
    return redirect("team-calendar")


@staff_member_required
@require_POST
def event_delete(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    _log(request, Activity.DELETE, f"el evento «{ev.title}»", reverse("team-calendar"))
    ev.delete()
    nxt = request.POST.get("next") or reverse("team-calendar")
    return redirect(nxt)


@staff_member_required
def events_json(request):
    events = [
        {
            "id": ev.id,
            "title": ev.title,
            "start": ev.start.isoformat(),
            "end": ev.end.isoformat() if ev.end else None,
            "allDay": ev.all_day,
        }
        for ev in Event.objects.all()
    ]
    return JsonResponse(events, safe=False)


def _activity_payload(limit=40):
    return [
        {
            "id": a.id,
            "user": a.user.get_username() if a.user else "alguien",
            "action": a.get_action_display(),
            "target": a.target,
            "url": a.url,
            "at": timezone.localtime(a.created_at).strftime("%d/%m %H:%M"),
            "kind": a.action,
        }
        for a in Activity.objects.select_related("user")[:limit]
    ]


@staff_member_required
def activity_json(request):
    return JsonResponse({"items": _activity_payload()})


@staff_member_required
def board(request):
    lists = TaskList.objects.prefetch_related("tasks__assignee")
    users = User.objects.filter(is_active=True).order_by("username")
    return render(
        request,
        "team/board.html",
        {"lists": lists, "users": users, "today": timezone.localdate()},
    )


@staff_member_required
@require_POST
def task_create(request):
    title = request.POST.get("title", "").strip()
    list_id = request.POST.get("list")
    assignee_id = request.POST.get("assignee") or None
    due = request.POST.get("due") or None
    note = request.POST.get("note", "").strip()
    if title and list_id:
        task_list = get_object_or_404(TaskList, pk=list_id)
        last = task_list.tasks.last()
        task = Task.objects.create(
            task_list=task_list,
            title=title,
            note=note,
            assignee_id=assignee_id,
            due=due or None,
            order=(last.order + 1) if last else 0,
            created_by=request.user,
        )
        _log(request, Activity.ADD, f"la tarea «{task.title}»", reverse("team-board"))
    return redirect("team-board")


@staff_member_required
@require_POST
def task_move(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_order = int(request.POST.get("order", task.order))
    list_id = request.POST.get("list")
    if list_id:
        task.task_list = get_object_or_404(TaskList, pk=list_id)
    task.order = new_order
    task.save(update_fields=["task_list", "order"])
    return JsonResponse({"ok": True})


@staff_member_required
@require_POST
def task_assign(request, pk):
    task = get_object_or_404(Task, pk=pk)
    assignee_id = request.POST.get("assignee") or None
    task.assignee_id = assignee_id
    task.save(update_fields=["assignee"])
    who = task.assignee.get_username() if task.assignee else "cualquiera"
    _log(request, Activity.CHANGE, f"la tarea «{task.title}» → asignada a {who}", reverse("team-board"))
    return redirect("team-board")


@staff_member_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    _log(request, Activity.DELETE, f"la tarea «{task.title}»", reverse("team-board"))
    task.delete()
    return redirect("team-board")


@staff_member_required
@require_POST
def list_create(request):
    name = request.POST.get("name", "").strip()
    if name:
        last = TaskList.objects.last()
        tl = TaskList.objects.create(name=name, order=(last.order + 1) if last else 0)
        _log(request, Activity.ADD, f"la lista «{tl.name}»", reverse("team-board"))
    return redirect("team-board")


@staff_member_required
@require_POST
def list_delete(request, pk):
    tl = get_object_or_404(TaskList, pk=pk)
    _log(request, Activity.DELETE, f"la lista «{tl.name}»", reverse("team-board"))
    tl.delete()
    return redirect("team-board")


# ---------- archivos ----------

def _files_context(folder):
    folders = Folder.objects.filter(parent=folder).select_related("created_by")
    files_qs = SharedFile.objects.filter(folder=folder).select_related("uploaded_by")
    crumbs = []
    node = folder.parent if folder else None
    while node:
        crumbs.append(node)
        node = node.parent
    crumbs.reverse()
    return {"folder": folder, "folders": folders, "files": files_qs, "crumbs": crumbs}


@staff_member_required
def files(request, folder_id=None):
    folder = get_object_or_404(Folder, pk=folder_id) if folder_id else None
    ctx = _files_context(folder)
    ctx["users"] = User.objects.filter(is_active=True)
    return render(request, "team/files.html", ctx)


@staff_member_required
@require_POST
def folder_create(request):
    name = request.POST.get("name", "").strip()
    parent_id = request.POST.get("parent") or None
    if name:
        parent = get_object_or_404(Folder, pk=parent_id) if parent_id else None
        f = Folder.objects.create(name=name, parent=parent, created_by=request.user)
        _log(request, Activity.ADD, f"la carpeta «{f.path_names()}»", reverse("team-files"))
        return redirect("team-files-folder", folder_id=f.pk)
    return redirect("team-files")


@staff_member_required
@require_POST
def file_upload(request):
    folder_id = request.POST.get("folder") or None
    folder = get_object_or_404(Folder, pk=folder_id) if folder_id else None
    files_uploaded = request.FILES.getlist("file")
    for f in files_uploaded:
        sf = SharedFile.objects.create(folder=folder, file=f, uploaded_by=request.user)
        _log(request, Activity.ADD, f"el archivo «{sf.filename}»", reverse("team-files"))
    if folder:
        return redirect("team-files-folder", folder_id=folder.pk)
    return redirect("team-files")


@staff_member_required
@require_POST
def file_delete(request, pk):
    sf = get_object_or_404(SharedFile, pk=pk)
    _log(request, Activity.DELETE, f"el archivo «{sf.filename}»", reverse("team-files"))
    folder_id = sf.folder_id
    sf.file.delete(save=False)
    sf.delete()
    if folder_id:
        return redirect("team-files-folder", folder_id=folder_id)
    return redirect("team-files")


@staff_member_required
def file_download(request, pk):
    sf = get_object_or_404(SharedFile, pk=pk)
    return FileResponse(sf.file.open("rb"), as_attachment=True, filename=sf.filename)


@staff_member_required
def meet(request):
    return render(request, "team/meet.html")


@staff_member_required
def logout_view(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect("/")
