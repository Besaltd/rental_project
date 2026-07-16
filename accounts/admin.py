from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role',
                    'phone', 'is_staff', 'is_deleted')
    list_filter = BaseUserAdmin.list_filter + ('is_deleted',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Weitere Informationen', {
         'fields': ('role', 'phone', 'is_deleted', 'deleted_at')}),
    )

    def get_queryset(self, request) -> models.QuerySet:

        return self.model.all_objects.all()
