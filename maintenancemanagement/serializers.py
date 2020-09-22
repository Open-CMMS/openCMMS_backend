from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import (
    Equipment, EquipmentType, Field, FieldObject, FieldValue, File, Task,
    TaskType,
)

"""
Serializers enable the link between front-end and back-end
"""


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'time', 'is_template', 'equipment', 'teams', 'task_type', 'files',
            'over'
        ]


class TaskTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskType
        fields = ['id', 'name', 'fields_groups']


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['id', 'file', 'is_manual']


class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'files']


class EquipmentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields_groups', 'equipment_set']

    def update(self, instance, validated_data):
        equipments = instance.equipment_set.all()

        for attr, value in validated_data.items():
            if attr == 'equipment_set':
                for e in equipments:
                    if e not in value:
                        e.delete()
                instance.equipment_set.set(value)
            elif attr == 'fields_groups':
                instance.fields_groups.set(value)
                instance._apply_()
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class FieldValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldValue
        fields = ['id', 'value', 'field']


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ['id', 'name', 'field_group']


class DescribedObjectRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `described_object` generic relationship.
    """

    def to_representation(self, value):
        """
        Serialize described_object to a simple textual representation.
        """
        if isinstance(value, Task):
            return "Task: " + str(value.id)
        elif isinstance(value, Equipment):
            return "Equipment: " + str(value.id)
        elif isinstance(value, TaskType):
            return "TaskType: " + str(value.id)
        raise Exception('Unexpected type of tagged object')

    def to_internal_value(self, data):
        return data


class FieldObjectSerializer(serializers.ModelSerializer):
    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())

    class Meta:
        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']

    def create(self, validated_data):
        return FieldObject.objects.create(
            content_type=ContentType.objects.get(
                model=self.validated_data['described_object'].partition(":")[0].lower()
            ),
            object_id=self.validated_data['described_object'].partition(":")[2],
            field=self.validated_data['field'],
            field_value=self.validated_data['field_value'],
            value=self.validated_data['value'],
            description=self.validated_data['description']
        )

    def update(self, instance, validated_data):
        instance.content_type = ContentType.objects.get(
            model=self.validated_data['described_object'].partition(":")[0].lower()
        )
        instance.object_id = self.validated_data['described_object'].partition(":")[2]
        instance.field = validated_data.get('created', instance.field)
        instance.field_value = validated_data.get('field_value', instance.field_value)
        instance.value = validated_data.get('value', instance.value)
        instance.description = validated_data.get('description', instance.description)
        return instance
