from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'last_name', 'first_name', 'gender', 'current_class', 'status', 'guardian_name', 'guardian_phone')
    list_filter = ('status', 'gender', 'current_class__class_level', 'current_class')
    search_fields = ('admission_number', 'first_name', 'last_name', 'guardian_name', 'guardian_phone')
    ordering = ('current_class', 'last_name', 'first_name')
    fieldsets = (
        ('Basic Bio Data', {
            'fields': ('admission_number', 'first_name', 'last_name', 'other_names', 'gender', 'date_of_birth', 'passport_photo')
        }),
        ('Academic Enrollment', {
            'fields': ('current_class', 'admission_date', 'status')
        }),
        ('Medical & Background', {
            'fields': ('blood_group', 'genotype', 'state_of_origin', 'nationality', 'residential_address')
        }),
        ('Parent / Guardian Details', {
            'fields': ('guardian_name', 'guardian_relationship', 'guardian_phone', 'guardian_email', 'guardian_address')
        }),
    )
