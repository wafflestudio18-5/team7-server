from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'description']


admin.site.register(UserProfile, UserProfileAdmin)
