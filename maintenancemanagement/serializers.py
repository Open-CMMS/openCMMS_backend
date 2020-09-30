from attr import field

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import (
    Equipment,
    EquipmentType,
    Field,
    FieldObject,
    FieldValue,
    File,
    Task,
)
"""
Serializers enable the link between front-end and back-end
"""

#############################################################################
############################## BASE SERIALIZER ##############################
#############################################################################


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over'
        ]


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
        raise Exception('Unexpected type of tagged object')

    def to_internal_value(self, data):
        return data


class FieldObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']


#############################################################################
############################# FIELD SERIALIZER ##############################
#############################################################################


class FieldValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ['id', 'name']


class FieldCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ['id', 'name', 'field_group']


#############################################################################
########################## FIELD OBJECT SERIALIZER ##########################
#############################################################################


class FieldObjectValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldObject
        fields = ['id', 'field', 'value', 'description']

    def validate(self, data):
        field_values = FieldValue.objects.filter(field=data.get("field"))
        if field_values:
            try:
                value = field_values.get(value=data.get("value")), None
                data.update({"value": None})
                data.update({"field_value": value})
                return data
            except:
                raise serializers.ValidationError({
                    'error': ("Value doesn't match a FieldValue of the given Field"),
                })
        data.update({"field_value": None})
        return data


class FieldObjectCreateSerializer(serializers.ModelSerializer):
    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())

    class Meta:
        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']


#############################################################################
########################## FIELD VALUE SERIALIZER ###########################
#############################################################################


class FieldValueValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldValue
        fields = ['id', 'value']


class FieldValueCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldValue
        fields = ['id', 'value', 'field']


#############################################################################
############################## TASK SERIALIZER ##############################
#############################################################################


class TaskDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = []


class TaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        exclude = []


#############################################################################
########################## EQUIPMENT SERIALIZER #############################
#############################################################################


class EquipmentDetailsSerializer(serializers.ModelSerializer):

    equipment_type = EquipmentTypeSerializer()
    files = FileSerializer(many=True)

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'files']


#############################################################################
########################## EQUIPMENTTYPE SERIALIZER #########################
#############################################################################


class EquipmentTypeDetailsSerializer(serializers.ModelSerializer):

    equipment_set = EquipmentSerializer(many=True)

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields_groups', 'equipment_set']


class EquipmentTypeValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'equipment_set']


class EquipmentTypeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'fields_groups', 'equipment_set']
