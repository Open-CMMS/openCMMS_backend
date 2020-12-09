"""This is the models file for our utilities."""
from maintenancemanagement.models import Equipment, FieldObject

from django.db import models


class DataProvider(models.Model):
    """Define a dataprovider."""

    name = models.CharField(max_length=100, default="", blank=False, null=False)
    file_name = models.CharField(max_length=100, blank=False, null=False)
    ip_address = models.CharField(max_length=100, blank=False, null=False)
    port = models.PositiveIntegerField(default=502, blank=True, null=True)
    equipment = models.ForeignKey(
        Equipment,
        verbose_name="Linked equipment",
        help_text="The equipment for which you wish to get value",
        related_name="dataprovider_set",
        related_query_name="dataprovider",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    field_object = models.ForeignKey(
        FieldObject,
        verbose_name="Linked field",
        help_text="The field for which you wish to update value",
        related_name="field_set",
        related_query_name="field_object",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    recurrence = models.CharField(max_length=100, blank=False, null=False)
    is_activated = models.BooleanField(default=True, blank=False, null=True)
    job_id = models.CharField(max_length=100, default='')

    def __str__(self):
        """Define string representation of a dataprovider."""
        return str(self.equipment) + ' / ' + str(self.field_object) + ' / '

    def __repr__(self):
        """Define the representation of a dataprovider."""
        return '<DataProvider: ' + "id={id}, name='{name}', filename='{file_name}', equipment=\
'{equipment_name}', field_object='{field_object_field_name}', ip_address={ip_address}, port={port}, recurrence=\
{recurrence}, is_activated={is_activated}, job_id={job_id}".format(
            id=self.id,
            name=self.name,
            file_name=self.file_name,
            equipment_name=self.equipment.name,
            field_object_field_name=self.field_object.field.name,
            ip_address=self.ip_address,
            port=self.port,
            recurrence=self.recurrence,
            is_activated=self.is_activated,
            job_id=self.job_id
        ) + '>'
