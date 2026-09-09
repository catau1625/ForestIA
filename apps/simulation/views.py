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
