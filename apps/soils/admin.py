from django.contrib import admin

from .models import Parcel, SoilLayer, SoilProfile


class SoilLayerInline(admin.TabularInline):
    model = SoilLayer
    extra = 1


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ("name", "area_ha", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(SoilProfile)
class SoilProfileAdmin(admin.ModelAdmin):
    list_display = ("parcel", "soil_type", "ph", "sampled_at")
    list_filter = ("soil_type",)
    inlines = [SoilLayerInline]
