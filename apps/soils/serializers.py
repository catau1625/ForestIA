from rest_framework import serializers

from .models import Parcel, SoilLayer, SoilProfile


class SoilLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilLayer
        fields = "__all__"


class SoilProfileSerializer(serializers.ModelSerializer):
    layers = SoilLayerSerializer(many=True, read_only=True)

    class Meta:
        model = SoilProfile
        fields = "__all__"


class ParcelSerializer(serializers.ModelSerializer):
    soil_profiles = SoilProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Parcel
        fields = "__all__"
