"""This file define all models concerning the maintenance management."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from usersmanagement.models import Team


class File(models.Model):
    """Define a file."""

    file = models.FileField(blank=False, null=False)
    is_manual = models.BooleanField(default=True)

    def __str__(self):
        """Define string representation of a file."""
        return self.file.name


class FieldGroup(models.Model):
    """Define a field group."""

    name = models.CharField(max_length=50)
    is_equipment = models.BooleanField(default=False)

    def __str__(self):
        """Define string representation of a field group."""
        return self.name


class Field(models.Model):
    """Define a field."""

    name = models.CharField(max_length=50)
    field_group = models.ForeignKey(
        FieldGroup,
        on_delete=models.CASCADE,
        related_name="field_set",
        related_query_name="field",
        null=True,
        blank=True
    )

    def __str__(self):
        """Define string representation of a field."""
        return self.name


class FieldValue(models.Model):
    """Define a field value."""

    value = models.CharField(max_length=100)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="value_set", related_query_name="value")

    def __str__(self):
        """Define string representation of a field value."""
        return self.value


class FieldObject(models.Model):
    """
    Define a field object.

    content_type and object_id allow described_object to \
        reference TaskType or EquipmentType
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    described_object = GenericForeignKey(
        'content_type', 'object_id'
    )  # pour ajouter on fera fo = FieldObject(described_object=taskType, ...)
    # où task type est une instance de tasktype

    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="object_set", related_query_name="object")

    field_value = models.ForeignKey(
        FieldValue,
        on_delete=models.SET_NULL,
        related_name="object_set",
        related_query_name="object",
        null=True,
        blank=True
    )

    value = models.CharField(max_length=100, default="", blank=True, null=True)

    description = models.CharField(max_length=100, default="", blank=True, null=True)

    def __str__(self):
        """Define string representation of a field object."""
        return self.value + str(self.field_value)


class EquipmentType(models.Model):
    """Define an equipment type."""

    name = models.CharField(max_length=100, unique=True)
    fields_groups = models.ManyToManyField(
        FieldGroup,
        verbose_name='Equipment Type Field',
        blank=True,
        help_text='Specific fields for this equipment type',
        related_name="equipmentType_set",
        related_query_name="equipmentType"
    )

    def __str__(self):
        """Define string representation of an equipment type."""
        return self.name


class Equipment(models.Model):
    """Define an equipment."""

    name = models.CharField(max_length=100)
    equipment_type = models.ForeignKey(
        EquipmentType,
        verbose_name="Equipment Type",
        on_delete=models.CASCADE,
        null=False,
        related_name="equipment_set",
        related_query_name="equipment"
    )

    files = models.ManyToManyField(
        File, verbose_name="Equipment File", related_name="equipment_set", related_query_name="equipment", blank=True
    )

    def __str__(self):
        """Define string representation of an equipment."""
        return self.name


class Task(models.Model):
    """Define a task."""

    name = models.CharField(max_length=100)
    end_date = models.DateField(null=True, blank=True)  # Correspond à la date butoire
    description = models.TextField(max_length=2000, default="")
    duration = models.DurationField(null=True, blank=True)  # Correspond à la durée forfaitaire
    is_template = models.BooleanField(default=False)
    equipment = models.ForeignKey(
        Equipment,
        verbose_name="Assigned equipment",
        help_text="The equipment assigned to the task",
        related_name="task_set",
        related_query_name="task",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    equipment_type = models.ForeignKey(
        EquipmentType,
        verbose_name="Assigned equipment type",
        help_text="The type of equipment assigned to the task",
        related_name="task_set",
        related_query_name="task",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    teams = models.ManyToManyField(
        Team,
        verbose_name="Assigned team(s)",
        blank=True,
        help_text="The team(s) assigned to this task",
        related_name="task_set",
        related_query_name="task",
    )
    files = models.ManyToManyField(
        File,
        verbose_name="Task File",
        related_name="task_set",
        related_query_name="task",
        blank=True,
    )
    over = models.NullBooleanField(default=False)
