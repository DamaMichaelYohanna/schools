from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class FeeCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='e.g. Tuition Fee, Development Levy, ICT & Lab Fee, PTA Levy'
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Fee Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    fee_category = models.ForeignKey(
        FeeCategory,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    class_level = models.ForeignKey(
        'academics.ClassLevel',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    academic_session = models.ForeignKey(
        'academics.AcademicSession',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    academic_term = models.ForeignKey(
        'academics.AcademicTerm',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ['fee_category', 'class_level', 'academic_session', 'academic_term']
        ordering = ['class_level', 'fee_category']

    def __str__(self):
        return f"{self.fee_category.name} - {self.class_level.name} ({self.amount})"


class Invoice(models.Model):
    class StatusChoices(models.TextChoices):
        PAID = 'PAID', 'Fully Paid'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        UNPAID = 'UNPAID', 'Unpaid'

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='e.g. INV-2025-0001'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    academic_session = models.ForeignKey(
        'academics.AcademicSession',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    academic_term = models.ForeignKey(
        'academics.AcademicTerm',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.UNPAID
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'academic_session', 'academic_term']
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.student.full_name} ({self.status})"

    def recalculate(self):
        total_paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        self.amount_paid = Decimal(str(total_paid))
        total = Decimal(str(self.total_amount or '0.00'))
        self.balance = max(Decimal('0.00'), total - self.amount_paid)

        if self.amount_paid >= total and total > Decimal('0.00'):
            self.status = self.StatusChoices.PAID
        elif self.amount_paid > Decimal('0.00'):
            self.status = self.StatusChoices.PARTIAL
        else:
            self.status = self.StatusChoices.UNPAID

        super().save(update_fields=['amount_paid', 'balance', 'status', 'updated_at'])

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            rand_code = uuid.uuid4().hex[:6].upper()
            self.invoice_number = f"INV-{year}-{rand_code}"
        
        total = Decimal(str(self.total_amount or '0.00'))
        paid = Decimal(str(self.amount_paid or '0.00'))
        self.total_amount = total
        self.amount_paid = paid
        self.balance = max(Decimal('0.00'), total - paid)
        
        if paid >= total and total > Decimal('0.00'):
            self.status = self.StatusChoices.PAID
        elif paid > Decimal('0.00'):
            self.status = self.StatusChoices.PARTIAL
        else:
            self.status = self.StatusChoices.UNPAID
        super().save(*args, **kwargs)


class Payment(models.Model):
    class MethodChoices(models.TextChoices):
        CASH = 'CASH', 'Cash'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        POS = 'POS', 'POS / Card'
        CHEQUE = 'CHEQUE', 'Bank Draft / Cheque'
        ONLINE = 'ONLINE', 'Online Payment'

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique official receipt number e.g. RCP-2025-0001'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=30,
        choices=MethodChoices.choices,
        default=MethodChoices.BANK_TRANSFER
    )
    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Bank reference / teller number / POS slip ref'
    )
    payment_date = models.DateField(default=timezone.now)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_payments',
        help_text='Accountant / Bursar who recorded the transaction'
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            year = timezone.now().year
            rand_code = uuid.uuid4().hex[:6].upper()
            self.receipt_number = f"RCP-{year}-{rand_code}"
        super().save(*args, **kwargs)
        self.invoice.recalculate()
