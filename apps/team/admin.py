from django.contrib import admin

from .models import Activity, Event, Folder, SharedFile, Task, TaskList


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "all_day", "created_by")
    list_filter = ("all_day",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at")
    list_filter = ("action",)


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    inlines = [TaskInline]


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_by")


@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "folder", "uploaded_by", "created_at", "size_kb")
