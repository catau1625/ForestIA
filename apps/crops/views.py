from rest_framework import viewsets

from .models import Plant
from .serializers import PlantSerializer


class PlantViewSet(viewsets.ModelViewSet):
    """CRUD de plantas. Sirve al menú de carga de cultivos."""

    queryset = Plant.objects.prefetch_related("stages").all()
    serializer_class = PlantSerializer
    filterset_fields = ["kind"]
    search_fields = ["name", "species"]
