from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="team-home"),
    path("calendario/", views.calendar, name="team-calendar"),
    path("eventos/nuevo/", views.event_create, name="team-event-create"),
    path("eventos/<int:pk>/editar/", views.event_update, name="team-event-update"),
    path("eventos/<int:pk>/borrar/", views.event_delete, name="team-event-delete"),
    path("eventos.json", views.events_json, name="team-events-json"),
    path("actividad.json", views.activity_json, name="team-activity-json"),
    path("tareas/", views.board, name="team-board"),
    path("tareas/nueva/", views.task_create, name="team-task-create"),
    path("tareas/<int:pk>/mover/", views.task_move, name="team-task-move"),
    path("tareas/<int:pk>/asignar/", views.task_assign, name="team-task-assign"),
    path("tareas/<int:pk>/borrar/", views.task_delete, name="team-task-delete"),
    path("tareas/lista/nueva/", views.list_create, name="team-list-create"),
    path("tareas/lista/<int:pk>/borrar/", views.list_delete, name="team-list-delete"),
    path("archivos/", views.files, name="team-files"),
    path("archivos/<int:folder_id>/", views.files, name="team-files-folder"),
    path("archivos/carpeta/nueva/", views.folder_create, name="team-folder-create"),
    path("archivos/subir/", views.file_upload, name="team-file-upload"),
    path("archivos/archivo/<int:pk>/mover/", views.file_move, name="team-file-move"),
    path("archivos/archivo/<int:pk>/borrar/", views.file_delete, name="team-file-delete"),
    path("archivos/descargar/<int:pk>/", views.file_download, name="team-file-download"),
    path("archivos/archivo/<int:pk>/ver/", views.file_preview, name="team-file-preview"),
    path("reuniones/", views.meet, name="team-meet"),
    path("salir/", views.logout_view, name="team-logout"),
]
