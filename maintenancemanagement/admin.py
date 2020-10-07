from django.contrib import admin

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

# Register your models here.

admin.site.register(File)
admin.site.register(FieldGroup)
admin.site.register(Task)
admin.site.register(Field)
admin.site.register(FieldValue)
admin.site.register(FieldObject)
admin.site.register(Equipment)
admin.site.register(EquipmentType)
