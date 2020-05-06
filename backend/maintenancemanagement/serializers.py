from rest_framework import serializers
from .models import Equipment, EquipmentType, File, Task, TaskType, FieldValue, Field


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

class FieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldValue
        fields = ['id','value','field']

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['id', 'name', 'field_group']
