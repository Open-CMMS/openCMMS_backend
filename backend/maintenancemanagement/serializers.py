from maintenancemanagement.models import Task, TaskType
from rest_framework import serializers

from rest_framework import serializers
from .models import Equipment, EquipmentType, File
"""
Serializers enable the link between front-end and back-end
"""

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'end_date', 'time', 'is_template', 'equipment', 'teams', 'task_type']

class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields= ['id', 'name', 'fields_groups']
        
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id','file','is_manual']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type','files']

class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields_groups']
