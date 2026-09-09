"""Parcelas, perfiles edáficos y capas de suelo."""
from django.db import models


class Parcel(models.Model):
    """Lote productivo georreferenciado."""

    name = models.CharField("nombre", max_length=120)
    # En producción migrar a PointField/ PolygonField de PostGIS.
    latitude = models.FloatField("latitud", null=True, blank=True)
    longitude = models.FloatField("longitud", null=True, blank=True)
    area_ha = models.FloatField("superficie (ha)", null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SoilProfile(models.Model):
    """Perfil edáfico de una parcela."""

    class SoilType(models.TextChoices):
        FRANCO = "franco", "Franco"
        ARENOSO = "arenoso", "Arenoso"
        ARCILLOSO = "arcilloso", "Arcilloso"
        FIBRA_COCO = "fibra_coco", "Fibra de coco (sustrato)"
        OTRO = "otro", "Otro"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="soil_profiles")
    soil_type = models.CharField("tipo de suelo", max_length=20, choices=SoilType.choices)
    ph = models.FloatField("pH", null=True, blank=True)
    organic_matter_pct = models.FloatField("materia orgánica (%)", null=True, blank=True)
    electrical_conductivity = models.FloatField("conductividad eléctrica (dS/m)", null=True, blank=True)
    sampled_at = models.DateField("fecha de muestreo", null=True, blank=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-sampled_at"]

    def __str__(self):
        return f"{self.parcel} · {self.get_soil_type_display()}"


class SoilLayer(models.Model):
    """Capa (horizonte) del perfil con sus propiedades hídricas."""

    profile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, related_name="layers")
    depth_from_cm = models.PositiveIntegerField("profundidad inicial (cm)")
    depth_to_cm = models.PositiveIntegerField("profundidad final (cm)")
    sand_pct = models.FloatField("arena (%)", null=True, blank=True)
    silt_pct = models.FloatField("limo (%)", null=True, blank=True)
    clay_pct = models.FloatField("arcilla (%)", null=True, blank=True)
    field_capacity_pct = models.FloatField("capacidad de campo (%)", null=True, blank=True)
    wilting_point_pct = models.FloatField("punto de marchitez (%)", null=True, blank=True)
    bulk_density = models.FloatField("densidad aparente (g/cm³)", null=True, blank=True)

    class Meta:
        ordering = ["depth_from_cm"]

    def __str__(self):
        return f"{self.profile} · {self.depth_from_cm}–{self.depth_to_cm} cm"
