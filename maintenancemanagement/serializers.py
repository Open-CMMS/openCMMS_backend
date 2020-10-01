from rest_framework import serializers

from .models import (
    Equipment,
    EquipmentType,
    Field,
    FieldGroup,
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


class FieldRequirementsSerializer(serializers.ModelSerializer):
    """This serializer serialize Fields in an explicite way.

    This serializer does not serialize the id of FieldValues associated to the
    Field serialized but serialize the values instead.

    Exemple of JSON we get by using it :
    {
        "id":5,
        "name":"Marque",
        "value":["Volvo", "Peugeot", "Ferrari"]
    }
    """

    value = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata.

        model is the Model the Serializer is associated to.
        fields represents the fields it serializes.
        """

        model = Field
        fields = ['id', 'name', 'value']

    def get_value(self, obj):
        """Get the values of the FieldValues associated with the Field as obj."""
        if obj.value_set.count() == 0:
            return []
        else:
            return obj.value_set.all().values_list('value', flat=True)


class TaskRequierementsSerializer(serializers.Serializer):

    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()

    class Meta:

        fields = ['trigger_conditions', 'end_conditions']

    def get_trigger_conditions(self, obj):

        trigger_fields = FieldGroup.objects.get(name='Trigger Conditions').field_set.all()
        return FieldRequirementsSerializer(trigger_fields, many=True).data

    def get_end_conditions(self, obj):
        end_fields = FieldGroup.objects.get(name='End Conditions').field_set.all()
        return FieldRequirementsSerializer(end_fields, many=True).data


class TaskTemplateRequirementsSerializer(TaskRequierementsSerializer, serializers.ModelSerializer):

    templates = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['trigger_conditions', 'end_conditions', 'templates']

    def get_templates(self, obj):
        templates = Task.objects.filter(is_template=True)
        return templates.values()


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


class EquipmentRequirementsSerializer(serializers.ModelSerializer):
    """This serializer serialize EquipementType in a explicite way.
    
    This serializer does not serialize the id of the Field of its
    EquipementType, but use the data of FieldRequirementsSerializer instead.

    Exemple of a JSON we get by using it :
    {
        "id":1,
        "name":"Voiture",
        "fields":[
            {
                "id":5,
                "name":"Marque",
                "value":["Volvo", "Peugeot", "Ferrari"]
            },
            {
                "id":6,
                "name":"Kilometrage",
                "value":[]
            }
        ]
    },
    {
        "id":3,
        "name":"Embouteilleuse",
        "fields":[
            {
                "id":5,
                "name":"Marque",
                "value":["GAI", "Bosch"]
            },
            {
                "id":6,
                "name":"Capacité",
                "value":[]
            }
        ]
    }
    """

    field = serializers.SerializerMethodField()

    # This would make more sens to use `fields`, but it does not work
    # so we use `field`.

    class Meta:
        """This class contains the serializer metadata.

        model is the Model the Serializer is associated to.
        fields represents the fields it serializes.
        """

        model = EquipmentType
        fields = ['id', 'name', 'field']

    def get_field(self, obj):
        """Get the explicit field associated with the EquipementType as obj. """
        fields = obj.fields_groups.all()
        return FieldRequirementsSerializer(fields, many=True).data


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
