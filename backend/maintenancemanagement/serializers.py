from rest_framework import serializers
from .models import Equipment, EquipmentType, Files
"""
Serializers enable the link between front-end and back-end
"""

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id','name','file','is_notice']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type','files']

class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields']
