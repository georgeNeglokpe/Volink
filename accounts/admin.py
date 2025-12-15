from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ('username', 'email', 'role', 'phone', 'course_department', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('role', 'phone', 'course_department')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {'fields': ('role', 'phone', 'course_department')}),
    )

