from django.db import models
from django.conf import settings
from decimal import Decimal


class SubjectResult(models.Model):
    """
    Score record for a student in a specific subject, class, session, and term.
    Uploaded / managed by the allocated subject teacher.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='subject_results'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='results'
    )
    class_section = models.ForeignKey(
        'academics.ClassSection',
        on_delete=models.CASCADE,
        related_name='results'
    )
    academic_session = models.ForeignKey(
        'academics.AcademicSession',
        on_delete=models.CASCADE,
        related_name='results'
    )
    academic_term = models.ForeignKey(
        'academics.AcademicTerm',
        on_delete=models.CASCADE,
        related_name='results'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_results'
    )

    # Assessments
    ca1 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='CA 1 (Max 15)')
    ca2 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='CA 2 (Max 15)')
    ca3 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='CA 3 / Project (Max 10)')
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='Exam (Max 60)')

    # Computed fields
    total = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    grade = models.CharField(max_length=5, blank=True)
    remark = models.CharField(max_length=40, blank=True)
    subject_position = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'academic_session', 'academic_term']
        ordering = ['student', 'subject']

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.code}: {self.total} ({self.grade})"

    def calculate_total_and_grade(self):
        ca1 = Decimal(str(self.ca1 or '0.00'))
        ca2 = Decimal(str(self.ca2 or '0.00'))
        ca3 = Decimal(str(self.ca3 or '0.00'))
        exam = Decimal(str(self.exam or '0.00'))
        self.ca1 = ca1
        self.ca2 = ca2
        self.ca3 = ca3
        self.exam = exam
        self.total = min(Decimal('100.00'), max(Decimal('0.00'), ca1 + ca2 + ca3 + exam))

        score = float(self.total)
        if score >= 75:
            self.grade = 'A1'
            self.remark = 'Excellent'
        elif score >= 70:
            self.grade = 'B2'
            self.remark = 'Very Good'
        elif score >= 65:
            self.grade = 'B3'
            self.remark = 'Good'
        elif score >= 60:
            self.grade = 'C4'
            self.remark = 'Credit'
        elif score >= 55:
            self.grade = 'C5'
            self.remark = 'Credit'
        elif score >= 50:
            self.grade = 'C6'
            self.remark = 'Credit'
        elif score >= 45:
            self.grade = 'D7'
            self.remark = 'Pass'
        elif score >= 40:
            self.grade = 'E8'
            self.remark = 'Pass'
        else:
            self.grade = 'F9'
            self.remark = 'Fail'

    def save(self, *args, **kwargs):
        self.calculate_total_and_grade()
        super().save(*args, **kwargs)


class TermReportSummary(models.Model):
    """
    Term-wide composite summary card per student including class position,
    overall percentage, teacher remarks, and principal remarks.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='term_reports'
    )
    class_section = models.ForeignKey(
        'academics.ClassSection',
        on_delete=models.CASCADE,
        related_name='term_reports'
    )
    academic_session = models.ForeignKey(
        'academics.AcademicSession',
        on_delete=models.CASCADE,
        related_name='term_reports'
    )
    academic_term = models.ForeignKey(
        'academics.AcademicTerm',
        on_delete=models.CASCADE,
        related_name='term_reports'
    )

    total_score = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'))
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    position = models.PositiveIntegerField(null=True, blank=True)
    total_students_in_class = models.PositiveIntegerField(default=0)

    # Attendance
    days_present = models.PositiveIntegerField(default=0)
    total_school_days = models.PositiveIntegerField(default=0)

    # Qualitative remarks
    teacher_remark = models.CharField(
        max_length=255,
        blank=True,
        default='A dedicated and hardworking student.'
    )
    principal_remark = models.CharField(
        max_length=255,
        blank=True,
        default='Promising result. Keep up the high standard.'
    )
    next_term_resumption = models.DateField(null=True, blank=True)

    is_published = models.BooleanField(
        default=True,
        help_text='Make report card accessible for printing/viewing'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'academic_session', 'academic_term']
        ordering = ['class_section', 'position', 'student']

    def __str__(self):
        return f"Report Card: {self.student.full_name} ({self.academic_term})"
