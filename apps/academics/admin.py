from django.contrib import admin
from .models import AcademicSession, AcademicTerm, ClassLevel, ClassSection, Subject, SubjectAllocation


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('term_type', 'session', 'start_date', 'end_date', 'is_current')
    list_filter = ('term_type', 'is_current', 'session')
    search_fields = ('term_type', 'session__name')


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'class_level', 'name', 'class_teacher', 'student_count')
    list_filter = ('class_level',)
    search_fields = ('name', 'class_level__name', 'class_teacher__first_name', 'class_teacher__last_name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_elective')
    list_filter = ('is_elective',)
    search_fields = ('name', 'code')


@admin.register(SubjectAllocation)
class SubjectAllocationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_section', 'teacher', 'academic_session')
    list_filter = ('academic_session', 'class_section__class_level', 'teacher')
    search_fields = ('subject__name', 'class_section__name', 'teacher__first_name', 'teacher__last_name')
