"""This module is to access utils from the built-in admin menu."""
from django.contrib import admin

from .models import DataProvider

# Register your models here.

admin.site.register(DataProvider)
