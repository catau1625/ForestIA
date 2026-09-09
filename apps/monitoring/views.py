from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DroneFlight, Sensor, SensorReading
from .serializers import (
    DroneFlightSerializer,
    SensorReadingIngestSerializer,
    SensorReadingSerializer,
    SensorSerializer,
)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    filterset_fields = ["parcel", "sensor_type", "is_active"]


class SensorReadingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """GET /api/v1/monitoring/readings/ · POST para ingestión telemétrica."""

    queryset = SensorReading.objects.select_related("sensor").all()
    filterset_fields = ["sensor"]

    def get_serializer_class(self):
        if self.action == "create":
            return SensorReadingIngestSerializer
        return SensorReadingSerializer

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Última lectura de cada sonda activa de una parcela."""
        parcel_id = request.query_params.get("parcel")
        sensors = Sensor.objects.filter(is_active=True)
        if parcel_id:
            sensors = sensors.filter(parcel_id=parcel_id)
        out = []
        for sensor in sensors:
            last = sensor.readings.first()
            if last:
                out.append(SensorReadingSerializer(last).data)
        return Response(out)


class DroneFlightViewSet(viewsets.ModelViewSet):
    queryset = DroneFlight.objects.all()
    serializer_class = DroneFlightSerializer
    filterset_fields = ["parcel"]
