"""Serializers."""
from maintenancemanagement.serializers import (
    EquipmentSerializer,
    FieldObjectSerializer,
)
from rest_framework import serializers

from .models import DataProvider


class DataProviderSerializer(serializers.ModelSerializer):
    """Basic dataprovider serializer."""

    equipment = EquipmentSerializer()
    field_object = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = DataProvider
        fields = ['id', 'name', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']


class DataProviderCreateSerializer(serializers.ModelSerializer):
    """DataProvider create Serialize."""

    class Meta:
        """This class contains the serializer metadata."""

        model = DataProvider
        fields = ['id', 'name', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']


class DataProviderDetailsSerializer(serializers.ModelSerializer):
    """DataProvider details Serialize."""

    equipment = EquipmentSerializer()
    field_object = FieldObjectSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = DataProvider
        fields = ['id', 'name', 'file_name', 'ip_address', 'equipment', 'field_object', 'recurrence', 'is_activated']
