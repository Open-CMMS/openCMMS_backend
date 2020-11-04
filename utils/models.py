"""This is the models file for our utilities."""
from django.db import models
from maintenancemanagement.models import Equipment, FieldObject


class DataProvider(models.Model):
    """Define a dataprovider."""

    name = models.CharField(max_length=100, default="", blank=False, null=False)
    file_name = models.CharField(max_length=100, blank=False, null=False)
    ip_address = models.CharField(max_length=100, blank=False, null=False)
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
    is_activated = models.BooleanField(default=True, blank=False, null=False)
    job_id = models.CharField(max_length=100, default='')

    def __str__(self):
        """Define string representation of a dataprovider."""
        return str(self.equipment) + ' / ' + str(self.field_object)
