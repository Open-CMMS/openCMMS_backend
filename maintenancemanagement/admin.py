from django.contrib import admin

from .models import FieldGroup, File

# Register your models here.

admin.site.register(File)
admin.site.register(FieldGroup)
