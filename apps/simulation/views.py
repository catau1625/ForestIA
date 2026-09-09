import json

from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from .models import SimulationRun
from .serializers import SimulationRunSerializer
from .tasks import run_simulation_task


class SimulationRunViewSet(viewsets.ModelViewSet):
    """Crear una corrida dispara la simulación en Celery de forma asíncrona."""

    queryset = SimulationRun.objects.select_related("parcel", "plant", "soil_profile").all()
    serializer_class = SimulationRunSerializer
    filterset_fields = ["parcel", "plant", "status"]

    def perform_create(self, serializer):
        run = serializer.save()
        run_simulation_task.delay(run.id)


def run_preview(request, pk: int):
    """Vista animada de la simulación: planta a escala y capas de suelo dinámicas."""
    run = get_object_or_404(
        SimulationRun.objects.select_related("parcel", "plant", "soil_profile"), pk=pk
    )
    stages = list(run.plant.stages.values("name", "day_start", "day_end"))
    return render(
        request,
        "simulation/preview.html",
        {"run": run, "stages_json": json.dumps(stages)},
    )
