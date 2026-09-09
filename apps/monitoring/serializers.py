from rest_framework import serializers

from .models import DroneFlight, Sensor, SensorReading


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = "__all__"


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = "__all__"


class SensorReadingIngestSerializer(serializers.ModelSerializer):
    """Serializador pensado para la ingestión desde las sondas LoRa/MQTT."""

    class Meta:
        model = SensorReading
        fields = ("sensor", "timestamp", "moisture_pct", "temperature_c", "ec_ds_m", "battery_pct")

    def validate_sensor(self, value):
        if not value.is_active:
            raise serializers.ValidationError("La sonda está inactiva.")
        return value


class DroneFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneFlight
        fields = "__all__"
