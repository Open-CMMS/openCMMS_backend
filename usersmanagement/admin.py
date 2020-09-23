from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Team, TeamType, UserProfile

# Register your models here.

admin.site.register(UserProfile, UserAdmin)
admin.site.register(TeamType)
admin.site.register(Team)
