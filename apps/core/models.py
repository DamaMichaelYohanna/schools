from django.db import models
from django.conf import settings


class SchoolSetting(models.Model):
    """
    Singleton model for dynamic school branding, details, and current academic configuration.
    Controlled directly by Admin / Principal via dashboard settings.
    """
    school_name = models.CharField(
        max_length=200,
        default='Apex Secondary School',
        help_text='Official school name shown on all headers, reports, and receipts'
    )
    school_motto = models.CharField(
        max_length=255,
        default='Knowledge, Character & Excellence',
        help_text='Official school motto / tagline'
    )
    school_logo = models.ImageField(
        upload_to='school_branding/',
        blank=True,
        null=True,
        help_text='Upload the official secondary school emblem / badge'
    )
    email = models.EmailField(default='admin@apexsecondary.edu.ng')
    phone = models.CharField(max_length=50, default='+234 802 345 6789')
    address = models.TextField(default='Plot 14 Academic Boulevard, Knowledge City')
    website = models.URLField(blank=True, default='https://apexsecondary.edu.ng')
    
    current_session = models.ForeignKey(
        'academics.AcademicSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='school_current_session',
        help_text='Current active academic session'
    )
    current_term = models.ForeignKey(
        'academics.AcademicTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='school_current_term',
        help_text='Current active academic term'
    )
    
    principal_signature = models.ImageField(
        upload_to='school_branding/',
        blank=True,
        null=True,
        help_text='Official digital signature for student report cards'
    )
    currency_symbol = models.CharField(
        max_length=10,
        default='₦',
        help_text='Currency symbol for school fees & accounting'
    )

    # Assessment Score Weighting (Continuous Assessment + Exam = 100)
    ca1_max = models.PositiveSmallIntegerField(default=15, help_text='Max CA 1 test score')
    ca2_max = models.PositiveSmallIntegerField(default=15, help_text='Max CA 2 test score')
    ca3_max = models.PositiveSmallIntegerField(default=10, help_text='Max CA 3 project/assignment score')
    exam_max = models.PositiveSmallIntegerField(default=60, help_text='Max Examination score')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School Setting'
        verbose_name_plural = 'School Settings'

    def __str__(self):
        return self.school_name

    def save(self, *args, **kwargs):
        # Enforce singleton pattern
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=150)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.action} by {self.user}"
