from django.db import models
from django.conf import settings


class AcademicSession(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
        help_text='e.g. 2025/2026'
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(
        default=False,
        help_text='Designate as current active academic session'
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class AcademicTerm(models.Model):
    class TermChoices(models.TextChoices):
        FIRST = '1st Term', '1st Term'
        SECOND = '2nd Term', '2nd Term'
        THIRD = '3rd Term', '3rd Term'

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='terms'
    )
    term_type = models.CharField(
        max_length=20,
        choices=TermChoices.choices,
        default=TermChoices.FIRST
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(
        default=False,
        help_text='Designate as current active term'
    )

    class Meta:
        unique_together = ['session', 'term_type']
        ordering = ['session', 'term_type']

    def __str__(self):
        return f"{self.session.name} - {self.term_type}"

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicTerm.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class ClassLevel(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='e.g. JSS 1, JSS 2, JSS 3, SSS 1, SSS 2, SSS 3'
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        help_text='Order sequence for promotion and display'
    )

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ClassSection(models.Model):
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    name = models.CharField(
        max_length=50,
        help_text='Section/Arm identifier (e.g. A, B, Gold, Science, Arts)'
    )
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_classes',
        limit_choices_to={'role': 'TEACHER'}
    )

    class Meta:
        unique_together = ['class_level', 'name']
        ordering = ['class_level__order', 'name']

    def __str__(self):
        return f"{self.class_level.name} {self.name}".strip()

    @property
    def display_name(self):
        return f"{self.class_level.name} {self.name}".strip()

    @property
    def student_count(self):
        return self.students.filter(status='ACTIVE').count()


class Subject(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='e.g. Mathematics, English Language, Physics'
    )
    code = models.CharField(
        max_length=15,
        unique=True,
        help_text='e.g. MTH, ENG, PHY, BIO'
    )
    is_elective = models.BooleanField(
        default=False,
        help_text='Whether this subject is an optional elective'
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubjectAllocation(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='allocations',
        limit_choices_to={'role': 'TEACHER'}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.CASCADE,
        related_name='subject_allocations'
    )
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['teacher', 'subject', 'class_section', 'academic_session']
        ordering = ['class_section', 'subject']

    def __str__(self):
        return f"{self.subject.name} - {self.class_section.display_name} ({self.teacher.full_name})"
