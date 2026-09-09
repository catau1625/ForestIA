from rest_framework import viewsets

from .models import WeatherRecord
from .serializers import WeatherRecordSerializer


class WeatherRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    filterset_fields = ["parcel", "source"]
