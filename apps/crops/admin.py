from django.contrib import admin

from .models import CropStage, Plant


class CropStageInline(admin.StackedInline):
    model = CropStage
    extra = 1


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "cycle_days", "root_depth_cm")
    list_filter = ("kind",)
    search_fields = ("name", "species")
    inlines = [CropStageInline]
