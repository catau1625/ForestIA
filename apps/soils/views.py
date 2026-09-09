from rest_framework import viewsets

from .models import Parcel, SoilProfile
from .serializers import ParcelSerializer, SoilProfileSerializer


class ParcelViewSet(viewsets.ModelViewSet):
    queryset = Parcel.objects.prefetch_related("soil_profiles__layers").all()
    serializer_class = ParcelSerializer
    search_fields = ["name"]


class SoilProfileViewSet(viewsets.ModelViewSet):
    queryset = SoilProfile.objects.prefetch_related("layers").all()
    serializer_class = SoilProfileSerializer
    filterset_fields = ["parcel", "soil_type"]
