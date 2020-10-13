"""Serializers enable the link between front-end and back-end."""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from usersmanagement.serializers import TeamSerializer

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

#############################################################################
############################## BASE SERIALIZER ##############################
#############################################################################


class TaskSerializer(serializers.ModelSerializer):
    """Basic task serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over'
        ]


class FileSerializer(serializers.ModelSerializer):
    """Basic file serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = File
        fields = ['id', 'file', 'is_manual']


class EquipmentSerializer(serializers.ModelSerializer):
    """Basic equipment serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'files']


class EquipmentTypeSerializer(serializers.ModelSerializer):
    """Basic equimpent type serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = EquipmentType
        fields = ['id', 'name', 'fields_groups']

    def update(self, instance, validated_data):
        """Redefine the update method."""
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
    """Basic field value serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldValue
        fields = ['id', 'value', 'field']


class FieldSerializer(serializers.ModelSerializer):
    """Basic field serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Field
        fields = ['id', 'name', 'field_group']


class FieldObjectSerializer(serializers.ModelSerializer):
    """Basic field object serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']


class DescribedObjectRelatedField(serializers.RelatedField):
    """A custom field to use for the `described_object` \
        generic relationship."""

    def to_representation(self, value):
        """Serialize described_object to a simple textual representation."""
        if isinstance(value, Task):
            return "Task: " + str(value.id)
        elif isinstance(value, Equipment):
            return "Equipment: " + str(value.id)
        raise Exception('Unexpected type of tagged object')

    def to_internal_value(self, data):
        """Redefine the to_internal_value method."""
        return data


class FieldObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']


#############################################################################
############################# FIELD SERIALIZER ##############################
#############################################################################


class FieldValidationSerializer(serializers.ModelSerializer):
    """Field validation serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Field
        fields = ['id', 'name']


class FieldCreateSerializer(serializers.ModelSerializer):
    """Field create serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Field
        fields = ['id', 'name', 'field_group']


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
        """This class contains the serializer metadata."""

        model = Field
        fields = ['id', 'name', 'value']

    def get_value(self, obj):
        """Get the values of the FieldValues associated \
            with the Field as obj."""
        if obj.value_set.count() == 0:
            return []
        else:
            return obj.value_set.all().values_list('value', flat=True)


#############################################################################
########################## FIELD OBJECT SERIALIZER ##########################
#############################################################################


class FieldObjectValidationSerializer(serializers.ModelSerializer):
    """Field object validation serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['field', 'value', 'description']

    def validate(self, data):
        """Redefine the validate method."""
        field_values = FieldValue.objects.filter(field=data.get("field"))
        if field_values:
            print("Il y a des fields values")
            try:
                value = field_values.get(value=data.get("value")), None
                data.update({"value": None})
                data.update({"field_value": value})
                return data
            except ObjectDoesNotExist:
                raise serializers.ValidationError({
                    'error': ("Value doesn't match a FieldValue of the given Field"),
                })
        elif data.get("value") is None:
            print("Il n'y en a pas")
            raise serializers.ValidationError({
                'error': ("Value required"),
            })
        data.update({"field_value": None})
        return data


class FieldObjectCreateSerializer(serializers.ModelSerializer):
    """Field object create serializer."""

    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['described_object', 'field', 'field_value', 'value', 'description']

    def validate(self, data):
        """Redefine the validate method."""
        field_values = FieldValue.objects.filter(field=data.get("field"))
        if field_values:
            value = field_values.get(value=data.get("value"))
            data.update({"value": ""})
            data.update({"field_value": value})
            return data
        data.update({"field_value": None})
        return data


class FieldObjectNewFieldValidationSerializer(serializers.ModelSerializer):

    name = serializers.CharField()

    class Meta:
        model = FieldObject
        fields = ['name', 'value', 'description']


class FieldObjectForTaskDetailsSerializer(serializers.ModelSerializer):

    field_name = serializers.CharField(source='field.name')
    value = serializers.SerializerMethodField()

    class Meta:
        model = FieldObject
        fields = ['id', 'field_name', 'value', 'description']

    def get_value(self, obj):
        if obj.field_value:
            return obj.field_value.value
        else:
            return obj.value


#############################################################################
########################## FIELD VALUE SERIALIZER ###########################
#############################################################################


class FieldValueValidationSerializer(serializers.ModelSerializer):
    """Field value validation serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldValue
        fields = ['id', 'value']


class FieldValueCreateSerializer(serializers.ModelSerializer):
    """Field value create serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldValue
        fields = ['id', 'value', 'field']


#############################################################################
############################## TASK SERIALIZER ##############################
#############################################################################


class TaskDetailsSerializer(serializers.ModelSerializer):

    equipment_type = EquipmentTypeSerializer()
    teams = TeamSerializer(many=True)
    equipment = EquipmentSerializer()
    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over',
            'trigger_conditions', 'end_conditions', 'equipment_type'
        ]

    def get_trigger_conditions(self, obj):
        content_type_object = ContentType.objects.get_for_model(obj)
        trigger_fields_objects = FieldObject.objects.filter(
            object_id=obj.id, content_type=content_type_object, field__field_group__name='Trigger Conditions'
        )
        return FieldObjectForTaskDetailsSerializer(trigger_fields_objects, many=True).data

    def get_end_conditions(self, obj):
        content_type_object = ContentType.objects.get_for_model(obj)
        end_fields_objects = FieldObject.objects.filter(
            object_id=obj.id, content_type=content_type_object, field__field_group__name='End Conditions'
        )
        return FieldObjectForTaskDetailsSerializer(end_fields_objects, many=True).data


class TemplateDetailsSerializer(serializers.ModelSerializer):

    equipment_type = EquipmentTypeSerializer()
    teams = TeamSerializer(many=True)
    equipment = EquipmentSerializer()
    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over',
            'trigger_conditions', 'end_conditions', 'equipment_type'
        ]

    def get_trigger_conditions(self, obj):
        content_type_object = ContentType.objects.get_for_model(obj)
        trigger_fields = Field.objects.filter(
            object__object_id=obj.id, object__content_type=content_type_object, field_group__name='Trigger Conditions'
        )
        return FieldRequirementsSerializer(trigger_fields, many=True).data

    def get_end_conditions(self, obj):
        content_type_object = ContentType.objects.get_for_model(obj)
        end_fields = Field.objects.filter(
            object__object_id=obj.id, object__content_type=content_type_object, field_group__name='End Conditions'
        )
        return FieldRequirementsSerializer(end_fields, many=True).data


class TaskTemplateRequirementsSerializer(serializers.Serializer):

    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()
    task_templates = serializers.SerializerMethodField()

    class Meta:
        fields = ['trigger_conditions', 'end_conditions', 'task_templates']

    def get_task_templates(self, obj):
        templates = Task.objects.filter(is_template=True)
        print(templates)
        serializer = TemplateDetailsSerializer(templates, many=True)
        print(serializer.data)
        return serializer.data

    def get_trigger_conditions(self, obj):
        trigger_fields = FieldGroup.objects.get(name='Trigger Conditions').field_set.all()
        print(trigger_fields)
        serializer = FieldRequirementsSerializer(trigger_fields, many=True)
        print(serializer.data)
        return serializer.data

    def get_end_conditions(self, obj):
        end_fields = FieldGroup.objects.get(name='End Conditions').field_set.all()
        return FieldRequirementsSerializer(end_fields, many=True).data


class TaskCreateSerializer(serializers.ModelSerializer):
    """Task creatre serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        exclude = []


class TaskListingSerializer(serializers.ModelSerializer):

    teams = TeamSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over'
        ]


#############################################################################
########################## EQUIPMENT SERIALIZER #############################
#############################################################################


class EquipmentFieldSerializer(serializers.ModelSerializer):

    field_name = serializers.CharField(source='field.name')
    field_value = FieldValueSerializer()

    class Meta:
        model = FieldObject
        fields = ['id', 'field', 'field_name', 'value', 'field_value', 'description']


class EquipmentDetailsSerializer(serializers.ModelSerializer):
    """Equipment details serializer."""

    equipment_type = EquipmentTypeSerializer()
    files = FileSerializer(many=True)
    field = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata."""

        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'files', 'field']

    def get_field(self, obj):
        """Get the explicit field associated with the \
            Equipement as obj. """

        content_type_object = ContentType.objects.get_for_model(obj)
        fields = FieldObject.objects.filter(object_id=obj.id, content_type=content_type_object)
        return EquipmentFieldSerializer(fields, many=True).data


class EquipmentCreateSerializer(serializers.ModelSerializer):
    """Equipment create serializer."""

    field = serializers.ListField(required=False)

    class Meta:
        """This class contains the serializer metadata."""

        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'files', 'field']


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
        """This class contains the serializer metadata."""

        model = EquipmentType
        fields = ['id', 'name', 'field']

    def get_field(self, obj):
        """Get the explicit field associated with the \
            EquipementType as obj."""
        fields_groups = obj.fields_groups.all()
        fields = []
        for fields_group in fields_groups:
            fields.extend(fields_group.field_set.all())
        return FieldRequirementsSerializer(fields, many=True).data


#############################################################################
########################## EQUIPMENTTYPE SERIALIZER #########################
#############################################################################


class EquipmentTypeDetailsSerializer(serializers.ModelSerializer):
    """Equipment type details serializer."""

    field = serializers.SerializerMethodField()
    equipments = EquipmentSerializer(source="equipment_set", many=True)

    # This would make more sens to use `fields`, but it does not work
    # so we use `field`.

    class Meta:
        """This class contains the serializer metadata."""

        model = EquipmentType
        fields = ['id', 'name', 'field', 'equipments']

    def get_field(self, obj):
        """Get the explicit field associated with the \
            EquipementType as obj."""
        fields_groups = obj.fields_groups.all()
        fields = []
        for fields_group in fields_groups:
            fields.extend(fields_group.field_set.all())
        return FieldRequirementsSerializer(fields, many=True).data


class EquipmentTypeValidationSerializer(serializers.ModelSerializer):
    """Equipment type validation serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = EquipmentType
        fields = ['id', 'name']


class EquipmentTypeCreateSerializer(serializers.ModelSerializer):
    """Equipment type create serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = EquipmentType
        fields = ['id', 'name', 'fields_groups']


class EquipmentTypeQuerySerializer(serializers.ModelSerializer):
    field = serializers.DictField(required=False)

    class Meta:
        """This class contains the serializer metadata.

        model is the Model the Serializer is associated to.
        fields represents the fields it serializes.
        """

        model = EquipmentType
        fields = ['id', 'name', 'field']
