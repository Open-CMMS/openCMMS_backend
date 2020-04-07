from django.contrib import admin
from .models import UserProfile,GroupType, Team
from django.contrib.auth.admin import UserAdmin

# Register your models here.

admin.site.register(UserProfile, UserAdmin)
admin.site.register(GroupType)
admin.site.register(Team)