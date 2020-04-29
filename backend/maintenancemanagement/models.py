from django.db import models
from usersmanagement.models import Team
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

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


class FieldValue(models.Model):
    value = models.CharField(max_length=100)
    field = models.ForeignKey(Field,
                              on_delete = models.CASCADE,
                              related_name="value_set",
                              related_query_name="value")

class FieldObject(models.Model):
    
    
    # Ces 3 attributs permettent de faire en sorte que described_object puisse référencer TaskType ou EquipmentType
    content_type = models.ForeignKey(ContentType, on_delete = models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    described_object = GenericForeignKey('content_type', 'object_id') # pour ajouter on fera fo = FieldObject(described_object=taskType, ...) où task type est une instance de tasktype


    field = models.ForeignKey(Field,
                            on_delete=models.CASCADE,
                            related_name="object_set",
                            related_query_name="object")

    field_value = models.ForeignKey(FieldValue,
                            on_delete=models.SET_NULL,
                            related_name="object_set",
                            related_query_name="object",
                            null=True)

    value = models.CharField(max_length=100, default="")


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
        related_query_name="files",
        blank=True)


class TaskType(models.Model):
    name = models.CharField(max_length=100)
    fields_groups = models.ManyToManyField(FieldGroup,
        verbose_name="Fields Group",
        help_text="Fields Groups of the Task Type",
        related_name="task_type_set",
        related_query_name="tasktype"
        )


#class Files(models.Model):
#    file = models.FileField()
#    is_notice = models.BooleanField(default=True)



class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000, default="")
    end_date = models.DateField() #Correspond à la date butoire
    time = models.DurationField() #Correspond à la durée forfaitaire
    is_template = models.BooleanField(default=False)
    equipment = models.ForeignKey(Equipment,
        verbose_name="Assigned equipment",
        help_text="The equipment assigned to the task", 
        related_name="task_set",
        related_query_name="task",
        on_delete = models.CASCADE,
        blank = True
        )
    teams = models.ManyToManyField(Team,
        verbose_name = "Assigned team(s)",
        blank = True,
        help_text = "The team(s) assigned to this task",
        related_name = "task_set",
        related_query_name = "task",
    )
    task_type = models.ForeignKey(TaskType,
        verbose_name="Task Type",
        on_delete=models.CASCADE,
        help_text='The type of this task',
        related_name="task_set",
        related_query_name="task",
        blank=True,
        )

    files = models.ManyToManyField(Files,
        verbose_name = "Files",
        related_name = "files_set",
        related_query_name="files",
        blank=True)




    
