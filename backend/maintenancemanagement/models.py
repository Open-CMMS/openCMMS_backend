from django.db import models
from django.db.models import FileField
from usersmanagement.models import Team
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    #gestion d'un fichier, voir pour en gérer plusieurs
    #upload = models.FileField(upload_to = 'uploads/equipment/')
