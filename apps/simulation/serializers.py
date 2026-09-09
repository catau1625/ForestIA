from rest_framework import serializers

from .models import SimulationRun


class SimulationRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationRun
        fields = "__all__"
        read_only_fields = ("status", "result", "created_at", "finished_at")
