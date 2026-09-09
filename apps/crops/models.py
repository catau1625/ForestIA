"""Modelos de plantas: especies, cultivos y demandas nutricionales por etapa."""
from django.db import models


class Plant(models.Model):
    """Especie/cultivo con sus parámetros agronómicos base."""

    class Kind(models.TextChoices):
        FRUTAL = "frutal", "Árbol frutal"
        HORTALIZA = "hortaliza", "Hortaliza"
        CEREAL = "cereal", "Cereal"
        OLEAGINOSA = "oleaginosa", "Oleaginosa"

    name = models.CharField("nombre", max_length=120)
    species = models.CharField("especie (latín)", max_length=160, blank=True)
    kind = models.CharField("tipo", max_length=20, choices=Kind.choices)
    cycle_days = models.PositiveIntegerField("duración del ciclo (días)")
    # Coeficientes de cultivo FAO-56
    kc_initial = models.FloatField("Kc inicial", default=0.4)
    kc_mid = models.FloatField("Kc etapa media", default=1.1)
    kc_end = models.FloatField("Kc final", default=0.6)
    root_depth_cm = models.PositiveIntegerField("profundidad radicular (cm)", default=40)
    growth_rate = models.FloatField("tasa de crecimiento (logística)", default=0.04)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CropStage(models.Model):
    """Etapa fenológica del cultivo con su demanda de nutrientes y agua."""

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField("etapa", max_length=80)  # ej. "Crecimiento vegetativo"
    order = models.PositiveIntegerField("orden", default=0)
    day_start = models.PositiveIntegerField("día inicial")
    day_end = models.PositiveIntegerField("día final")
    water_demand_mm_day = models.FloatField("demanda hídrica (mm/día)")
    nitrogen_ppm = models.FloatField("extracción de N (ppm)")
    phosphorus_ppm = models.FloatField("extracción de P (ppm)", default=0)
    potassium_ppm = models.FloatField("extracción de K (ppm)", default=0)

    class Meta:
        ordering = ["plant", "order"]

    def __str__(self):
        return f"{self.plant} · {self.name}"
