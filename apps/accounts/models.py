from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        PRINCIPAL = 'PRINCIPAL', 'Principal / Administrator'
        TEACHER = 'TEACHER', 'Teacher / Subject Instructor'
        ACCOUNTANT = 'ACCOUNTANT', 'Accountant / Bursar'
        ADMIN = 'ADMIN', 'Super Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TEACHER,
        help_text='Designated system role and access permission level'
    )
    staff_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text='Unique Staff Identification Number (e.g. STF-2025-001)'
    )
    phone_number = models.CharField(max_length=25, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True
    )
    avatar = models.ImageField(upload_to='staff_avatars/', blank=True, null=True)
    qualification = models.CharField(
        max_length=150,
        blank=True,
        help_text='e.g. B.Ed Mathematics, M.Sc English'
    )
    date_employed = models.DateField(null=True, blank=True)
    is_active_staff = models.BooleanField(default=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Staff / User'
        verbose_name_plural = 'Staff Members / Users'

    def __str__(self):
        full = self.get_full_name()
        if full:
            return f"{full} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        name = self.get_full_name()
        return name if name else self.username

    @property
    def is_principal(self):
        return self.role in [self.Role.PRINCIPAL, self.Role.ADMIN] or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT
