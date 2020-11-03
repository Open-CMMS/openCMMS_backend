"""Serializers."""
from maintenancemanagement.models import Equipment, FieldObject
from maintenancemanagement.serializers import (
    EquipmentSerializer,
    FieldObjectSerializer,
)
from rest_framework import serializers

from .models import Plugin


class PluginSerializer(serializers.ModelSerializer):
    """Basic plugin serializer."""

    equipment = EquipmentSerializer()
    field_object = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['id', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']


class PluginCreateSerializer(serializers.ModelSerializer):
    """Plugin create Serialize."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['id', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']


class PluginDetailsSerializer(serializers.ModelSerializer):
    """Plugin details Serialize."""

    equipment = EquipmentSerializer()
    field_object = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = Plugin
        fields = ['id', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']
