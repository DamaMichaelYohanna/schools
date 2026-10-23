from django.contrib import admin
from .models import FeeCategory, FeeStructure, Invoice, Payment


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('fee_category', 'class_level', 'academic_session', 'academic_term', 'amount')
    list_filter = ('academic_session', 'academic_term', 'class_level', 'fee_category')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('receipt_number', 'amount', 'payment_method', 'payment_date', 'received_by')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student', 'academic_session', 'academic_term', 'total_amount', 'amount_paid', 'balance', 'status')
    list_filter = ('status', 'academic_session', 'academic_term')
    search_fields = ('invoice_number', 'student__first_name', 'student__last_name', 'student__admission_number')
    readonly_fields = ('amount_paid', 'balance', 'status')
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'invoice', 'amount', 'payment_method', 'payment_date', 'received_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('receipt_number', 'transaction_reference', 'invoice__student__first_name', 'invoice__student__last_name')
