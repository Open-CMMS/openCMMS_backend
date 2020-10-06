from django.contrib import admin

from .models import FieldGroup, File, Task

# Register your models here.

admin.site.register(File)
admin.site.register(FieldGroup)
admin.site.register(Task)
