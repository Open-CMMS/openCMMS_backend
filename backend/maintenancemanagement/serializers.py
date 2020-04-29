from rest_framework import serializers
from .models import Equipment, EquipmentType
"""
Serializers enable the link between front-end and back-end
"""

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type']

class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields']