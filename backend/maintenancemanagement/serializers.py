from maintenancemanagement.models import Task, TaskType
from rest_framework import serializers

from rest_framework import serializers
from .models import Equipment, EquipmentType
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
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type']

class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields']
