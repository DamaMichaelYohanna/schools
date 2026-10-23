from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'staff_id', 'first_name', 'last_name', 'role', 'is_active_staff', 'is_staff')
    list_filter = ('role', 'is_active_staff', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'staff_id', 'email')
    ordering = ('role', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Secondary School Staff Attributes', {
            'fields': ('role', 'staff_id', 'phone_number', 'gender', 'avatar', 'qualification', 'date_employed', 'is_active_staff', 'address')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Secondary School Staff Attributes', {
            'fields': ('role', 'staff_id', 'first_name', 'last_name', 'email', 'phone_number', 'qualification')
        }),
    )
