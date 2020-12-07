"""Serializers enable the link between front-end and back-end."""

import imghdr

from PyPDF4.pdf import PdfFileReader

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

TRIGGER_CONDITIONS = 'Trigger Conditions'
END_CONDITIONS = 'End Conditions'

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

    def validate_file(self, file):
        """Check that the file sent is an image with imghdr or if it is a pdf."""
        if not imghdr.what(file):
            try:
                from io import BytesIO
                PdfFileReader(BytesIO(file.read()))
            except Exception:
                raise serializers.ValidationError('File should be an image or a pdf.')
        return file


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
    """Basic field object serializer."""

    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())
    name = serializers.CharField(source='field.name')

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description', 'name']


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
            try:
                value = field_values.get(value=data.get("value")), None
                data.update({"value": None})
                data.update({"field_value": value})
                return data
            except ObjectDoesNotExist:
                raise serializers.ValidationError({
                    'error': ("Value doesn't match a FieldValue of the given Field"),
                })
        elif data.get("value") is None and data.get("field").field_group.name == "Trigger Conditions":
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


class FieldObjectUpdateSerializer(serializers.ModelSerializer):
    """Field object create serializer."""

    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['id', 'described_object', 'field', 'field_value', 'value', 'description']

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
    """Field object validation serializer for new field."""

    name = serializers.CharField()

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['name', 'value', 'description']


class FieldObjectForTaskDetailsSerializer(serializers.ModelSerializer):
    """Field object details serializer for task."""

    field_name = serializers.CharField(source='field.name')
    value = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['id', 'field_name', 'value', 'description']

    def get_value(self, obj):
        """Give the value of a field object."""
        if obj.field_value:
            return obj.field_value.value
        else:
            return obj.value


class TriggerConditionsValidationSerializer(serializers.ModelSerializer):
    """Trigger condition validation serializer."""

    delay = serializers.CharField()
    field_object_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['field', 'value', 'description', 'delay', 'field_object_id']

    def validate(self, data):
        """Redefine the validate method."""
        if data.get('field').name in [
            'Above Threshold', 'Under Threshold', 'Frequency'
        ] and 'field_object_id' not in data:
            raise serializers.ValidationError(
                f'Misses field_object_id for {data.get("field").name} trigger condition.'
            )
        return data


class TriggerConditionsCreateSerializer(serializers.ModelSerializer):
    """Trigger condition create serializer."""

    delay = serializers.CharField()
    field_object_id = serializers.IntegerField(allow_null=True, required=False)
    described_object = DescribedObjectRelatedField(queryset=FieldObject.objects.all())

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['described_object', 'field', 'field_value', 'value', 'description', 'delay', 'field_object_id']

    def validate(self, data):
        """Redefine the validate method."""
        if data.get('field').name == 'Recurrence':
            value = f'{data.get("value")}|{data.get("delay")}'
        else:  #  data.get('field').name == 'Above Threshold':
            value = f'{data.get("value")}|{data.get("field_object_id")}|{data.get("delay")}'
        data.update({"value": value})
        data.update({"field_value": None})
        data.pop("delay")
        if 'field_object_id' in data:
            data.pop('field_object_id')
        return data


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
    """Task details serializer."""

    equipment_type = EquipmentTypeSerializer()
    teams = TeamSerializer(many=True)
    equipment = EquipmentSerializer()
    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()
    files = FileSerializer(many=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over',
            'trigger_conditions', 'end_conditions', 'equipment_type'
        ]

    def get_trigger_conditions(self, obj):
        """Return trigger conditions of the given task."""
        content_type_object = ContentType.objects.get_for_model(obj)
        trigger_fields_objects = FieldObject.objects.filter(
            object_id=obj.id, content_type=content_type_object, field__field_group__name=TRIGGER_CONDITIONS
        )
        return FieldObjectForTaskDetailsSerializer(trigger_fields_objects, many=True).data

    def get_end_conditions(self, obj):
        """Return end conditions of the given task."""
        content_type_object = ContentType.objects.get_for_model(obj)
        end_fields_objects = FieldObject.objects.filter(
            object_id=obj.id, content_type=content_type_object, field__field_group__name=END_CONDITIONS
        )
        return FieldObjectForTaskDetailsSerializer(end_fields_objects, many=True).data

    def get_duration(self, obj):
        """Return duration of the given task."""
        duration = obj.duration
        if duration is not None:
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) - hours * 60

            result = ""
            if days != 0:
                result += str(days) + 'd '
            if hours != 0:
                result += str(hours) + 'h '
            if minutes != 0:
                result += str(minutes) + 'm'

            if result != "" and result[-1] == ' ':
                result = result[:-1]

            return result
        else:
            return ''


class TemplateDetailsSerializer(serializers.ModelSerializer):
    """Task template details serializer."""

    equipment_type = EquipmentTypeSerializer()
    teams = TeamSerializer(many=True)
    equipment = EquipmentSerializer()
    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    files = FileSerializer(many=True)

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over',
            'trigger_conditions', 'end_conditions', 'equipment_type'
        ]

    def get_trigger_conditions(self, obj):
        """Return trigger conditions of the given task template."""
        content_type_object = ContentType.objects.get_for_model(obj)
        trigger_fields = Field.objects.filter(
            object__object_id=obj.id, object__content_type=content_type_object, field_group__name=TRIGGER_CONDITIONS
        )
        return FieldRequirementsSerializer(trigger_fields, many=True).data

    def get_end_conditions(self, obj):
        """Return end conditions of the given task template."""
        content_type_object = ContentType.objects.get_for_model(obj)
        end_fields = Field.objects.filter(
            object__object_id=obj.id, object__content_type=content_type_object, field_group__name=END_CONDITIONS
        )
        return FieldRequirementsSerializer(end_fields, many=True).data

    def get_duration(self, obj):
        """Return duration of the given task template."""
        duration = obj.duration
        if duration is not None:
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) - hours * 60

            result = ""
            if days != 0:
                result += str(days) + 'd '
            if hours != 0:
                result += str(hours) + 'h '
            if minutes != 0:
                result += str(minutes) + 'm'

            if result != "" and result[-1] == ' ':
                result = result[:-1]
            return result
        else:
            return ''


class TaskTemplateRequirementsSerializer(serializers.Serializer):
    """Task template requirements serializer."""

    trigger_conditions = serializers.SerializerMethodField()
    end_conditions = serializers.SerializerMethodField()
    task_templates = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata."""

        fields = ['trigger_conditions', 'end_conditions', 'task_templates']

    def get_task_templates(self, obj):
        """Give task template data."""
        templates = Task.objects.filter(is_template=True)
        serializer = TemplateDetailsSerializer(templates, many=True)
        return serializer.data

    def get_trigger_conditions(self, obj):
        """Return trigger conditions of the given task template."""
        trigger_fields = FieldGroup.objects.get(name=TRIGGER_CONDITIONS).field_set.all()
        serializer = FieldRequirementsSerializer(trigger_fields, many=True)
        return serializer.data

    def get_end_conditions(self, obj):
        """Return end conditions of the given task template."""
        end_fields = FieldGroup.objects.get(name=END_CONDITIONS).field_set.all()
        return FieldRequirementsSerializer(end_fields, many=True).data


class TaskCreateSerializer(serializers.ModelSerializer):
    """Task creatre serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        exclude = []


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Task creatre serializer."""

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        exclude = []


class TaskListingSerializer(serializers.ModelSerializer):
    """Task listing serializer."""

    teams = TeamSerializer(many=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        """This class contains the serializer metadata."""

        model = Task
        fields = [
            'id', 'name', 'description', 'end_date', 'duration', 'is_template', 'equipment', 'teams', 'files', 'over'
        ]

    def get_duration(self, obj):
        """Return duration of the given task."""
        duration = obj.duration
        if duration is not None:
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) - hours * 60

            result = ""
            if days != 0:
                result += str(days) + 'd '
            if hours != 0:
                result += str(hours) + 'h '
            if minutes != 0:
                result += str(minutes) + 'm'

            if result != "" and result[-1] == ' ':
                result = result[:-1]

            return result
        else:
            return ''


#############################################################################
########################## EQUIPMENT SERIALIZER #############################
#############################################################################


class EquipmentFieldSerializer(serializers.ModelSerializer):
    """Equipment field serializer."""

    field_name = serializers.CharField(source='field.name')
    field_value = FieldValueSerializer()

    class Meta:
        """This class contains the serializer metadata."""

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
            Equipement as obj."""
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


class EquipmentUpdateSerializer(serializers.ModelSerializer):
    """Equipment update serializer."""

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


class EquipmentFieldDataProviderSerializer(serializers.ModelSerializer):
    """Equipment field serializer."""

    name = serializers.CharField(source='field.name')
    field_value = FieldValueSerializer()

    class Meta:
        """This class contains the serializer metadata."""

        model = FieldObject
        fields = ['id', 'field', 'name', 'value', 'field_value', 'description']


class EquipmentDetailsDataProviderSerializer(serializers.ModelSerializer):
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
            Equipement as obj."""
        content_type_object = ContentType.objects.get_for_model(obj)
        fields = FieldObject.objects.filter(object_id=obj.id, content_type=content_type_object)
        return EquipmentFieldDataProviderSerializer(fields, many=True).data


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
    """Equipment type query serializer."""

    field = serializers.DictField(required=False)

    class Meta:
        """This class contains the serializer metadata.

        model is the Model the Serializer is associated to.
        fields represents the fields it serializes.
        """

        model = EquipmentType
        fields = ['id', 'name', 'field']
