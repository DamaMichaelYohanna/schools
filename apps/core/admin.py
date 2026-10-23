from django.contrib import admin
from .models import SchoolSetting, AuditLog


@admin.register(SchoolSetting)
class SchoolSettingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'email', 'phone', 'current_session', 'current_term', 'updated_at')
    fieldsets = (
        ('School Identity & Branding', {
            'fields': ('school_name', 'school_motto', 'school_logo', 'principal_signature')
        }),
        ('Contact & Location', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Academic & Grading Configuration', {
            'fields': ('current_session', 'current_term', 'currency_symbol', 'ca1_max', 'ca2_max', 'ca3_max', 'exam_max')
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating multiple instances (singleton)
        return not SchoolSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'details', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('action', 'details', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')

    def has_add_permission(self, request):
        return False
