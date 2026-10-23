from django.contrib import admin
from .models import SubjectResult, TermReportSummary


@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'class_section', 'academic_session', 'academic_term', 'ca1', 'ca2', 'ca3', 'exam', 'total', 'grade', 'remark')
    list_filter = ('academic_session', 'academic_term', 'class_section', 'subject', 'grade')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number', 'subject__name')
    readonly_fields = ('total', 'grade', 'remark')


@admin.register(TermReportSummary)
class TermReportSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_section', 'academic_session', 'academic_term', 'total_score', 'average_score', 'position', 'is_published')
    list_filter = ('academic_session', 'academic_term', 'class_section', 'is_published')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number')
