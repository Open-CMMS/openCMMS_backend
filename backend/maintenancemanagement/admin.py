from django.contrib import admin
from maintenancemanagement.models import FieldObject, Field, FieldValue, FieldGroup, Task, Equipment, EquipmentType

# Register your models here.

admin.site.register(FieldObject)
admin.site.register(Field)
admin.site.register(FieldValue)
admin.site.register(FieldGroup)
admin.site.register(Task)
admin.site.register(Equipment)
admin.site.register(EquipmentType)