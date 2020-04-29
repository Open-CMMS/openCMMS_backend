from django.db import models
from django.db.models import FileField

class Files(models.Model):
    """
        Define a file
    """
    file = models.FileField(blank=False, null=False)
    is_notice = models.BooleanField(default=True)
    def __str__(self):
        return self.file.name


class FieldGroup(models.Model):
    name = models.CharField(max_length=50)
    is_equipment = models.BooleanField(default=False)


class Field(models.Model):
    name = models.CharField(max_length=50)
    field_group = models.ForeignKey(FieldGroup,
                                    on_delete = models.CASCADE,
                                    related_name="field_set",
                                    related_query_name="field")

class EquipmentType(models.Model):
    """
        Define an equipment type
    """
    name = models.CharField(max_length=100)
    fields = models.ManyToManyField(Field,
        verbose_name='Equipment Type Field',
        blank=True,
        help_text='Specific fields for this equipment type',
        related_name="equipmentType_set",
        related_query_name="equipmentType")

class Equipment(models.Model):
    """
        Define an equipment.
    """
    name = models.CharField(max_length=100)
    equipment_type = models.ForeignKey(EquipmentType,
        verbose_name = "Equipment Type",
        on_delete = models.CASCADE,
        null = False,
        related_name = "equipment_set",
        related_query_name="equipment")
    files = models.ManyToManyField(Files,
        verbose_name = "Files",
        related_name = "files_set",
        related_query_name="files")
