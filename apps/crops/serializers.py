from rest_framework import serializers

from .models import CropStage, Plant


class CropStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropStage
        fields = "__all__"


class PlantSerializer(serializers.ModelSerializer):
    stages = CropStageSerializer(many=True, read_only=True)

    class Meta:
        model = Plant
        fields = "__all__"
