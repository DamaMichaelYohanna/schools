from django.db import models
from django.utils import timezone
from datetime import date


class Student(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active / Enrolled'
        GRADUATED = 'GRADUATED', 'Graduated / Alumni'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn / Transferred'

    admission_number = models.CharField(
        max_length=40,
        unique=True,
        help_text='Unique Student Admission Number (e.g. SEC/2025/001)'
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    other_names = models.CharField(max_length=60, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    date_of_birth = models.DateField(help_text='Date of birth (YYYY-MM-DD)')
    admission_date = models.DateField(default=timezone.now)

    current_class = models.ForeignKey(
        'academics.ClassSection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    passport_photo = models.ImageField(
        upload_to='students/passports/',
        blank=True,
        null=True,
        help_text='Official student passport photograph'
    )

    # Health & Bio Info
    blood_group = models.CharField(
        max_length=10,
        blank=True,
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')]
    )
    genotype = models.CharField(
        max_length=10,
        blank=True,
        choices=[('AA', 'AA'), ('AS', 'AS'), ('SS', 'SS'), ('AC', 'AC')]
    )
    state_of_origin = models.CharField(max_length=60, blank=True)
    nationality = models.CharField(max_length=60, default='Nigerian')
    residential_address = models.TextField(blank=True)

    # Parent / Guardian Information
    guardian_name = models.CharField(max_length=120)
    guardian_relationship = models.CharField(max_length=50, default='Parent')
    guardian_phone = models.CharField(max_length=30)
    guardian_email = models.EmailField(blank=True)
    guardian_address = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['current_class', 'last_name', 'first_name']

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"

    @property
    def full_name(self):
        if self.other_names:
            return f"{self.last_name}, {self.first_name} {self.other_names}"
        return f"{self.last_name}, {self.first_name}"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
