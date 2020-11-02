"""Serializers."""
from maintenancemanagement.serializers import (
    EquipmentSerializer,
    FieldObjectSerializer,
)
from rest_framework import serializers

from .models import Plugin


class PluginSerializer(serializers.ModelSerializer):
    """Basic plugin serializer."""

    equipment = EquipmentSerializer()
    field = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['file_name', 'ip_address', 'equipment', 'field', 'recurrence', 'activated']


class PluginCreateSerializer(serializers.ModelSerializer):
    """Plugin create Serialize."""

    equipment = EquipmentSerializer()
    field = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['file_name', 'ip_address', 'equipment', 'field', 'recurrence', 'activated']


class PluginDetailsSerializer(serializers.ModelSerializer):
    """Plugin details Serialize."""

    equipment = EquipmentSerializer()
    field = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['file_name', 'ip_address', 'equipment', 'field', 'recurrence', 'activated']
