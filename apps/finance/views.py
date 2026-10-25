from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from decimal import Decimal

from .models import Invoice, Payment, FeeCategory, FeeStructure
from .forms import PaymentRecordForm, InvoiceGenerateForm, FeeStructureForm, FeeCategoryForm
from apps.accounts.decorators import accountant_required
from apps.students.models import Student
from apps.academics.models import ClassSection, AcademicSession, AcademicTerm
from apps.core.models import SchoolSetting, AuditLog


@login_required
@accountant_required
def finance_dashboard_view(request):
    setting = SchoolSetting.load()
    
    fin_stats = Invoice.objects.aggregate(
        total_invoiced=Sum('total_amount'),
        total_paid=Sum('amount_paid'),
        total_balance=Sum('balance')
    )
    total_invoiced = fin_stats['total_invoiced'] or Decimal('0.00')
    total_collected = fin_stats['total_paid'] or Decimal('0.00')
    total_outstanding = fin_stats['total_balance'] or Decimal('0.00')

    collection_rate = 0
    if total_invoiced > 0:
        collection_rate = round((total_collected / total_invoiced) * 100, 1)

    method_breakdown = Payment.objects.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    recent_payments = Payment.objects.select_related('invoice__student', 'received_by')[:10]
    unpaid_invoices = Invoice.objects.filter(status__in=['UNPAID', 'PARTIAL']).select_related('student', 'academic_term')[:8]

    return render(request, 'finance/dashboard.html', {
        'total_invoiced': total_invoiced,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'collection_rate': collection_rate,
        'method_breakdown': method_breakdown,
        'recent_payments': recent_payments,
        'unpaid_invoices': unpaid_invoices,
        'setting': setting,
    })


@login_required
@accountant_required
def invoices_list_view(request):
    status = request.GET.get('status', '')
    class_id = request.GET.get('class_id', '')
    query = request.GET.get('q', '').strip()

    invoices = Invoice.objects.select_related('student__current_class__class_level', 'academic_term').all()

    if status:
        invoices = invoices.filter(status=status)

    if class_id:
        invoices = invoices.filter(student__current_class_id=class_id)

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__admission_number__icontains=query)
        )

    classes = ClassSection.objects.select_related('class_level').order_by('class_level__order', 'name')
    paginator = Paginator(invoices, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'finance/invoice_list.html', {
        'page_obj': page_obj,
        'classes': classes,
        'selected_class': class_id,
        'selected_status': status,
        'query': query,
    })


@login_required
@accountant_required
def invoice_detail_view(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('student__current_class__class_level', 'academic_session', 'academic_term'),
        pk=pk
    )
    payments = invoice.payments.select_related('received_by').order_by('-payment_date', '-created_at')

    fee_items = []
    if invoice.student.current_class and invoice.student.current_class.class_level:
        fee_items = FeeStructure.objects.filter(
            class_level=invoice.student.current_class.class_level,
            academic_session=invoice.academic_session,
            academic_term=invoice.academic_term
        ).select_related('fee_category').order_by('fee_category__name')

    return render(request, 'finance/invoice_detail.html', {
        'invoice': invoice,
        'payments': payments,
        'fee_items': fee_items,
    })


@login_required
@accountant_required
def invoice_delete_view(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('student', 'academic_session', 'academic_term'),
        pk=pk
    )

    has_payments = invoice.payments.exists() or invoice.amount_paid > Decimal('0.00')

    if request.method == 'POST':
        if has_payments:
            messages.error(
                request,
                f"Cannot delete Invoice #{invoice.invoice_number} because {invoice.payments.count()} payment receipt(s) have been issued against it. Accounting rules require payments to be reversed or refunded first."
            )
            return redirect('finance:invoice_detail', pk=invoice.pk)

        invoice_num = invoice.invoice_number
        student_name = invoice.student.full_name
        invoice.delete()

        AuditLog.objects.create(
            user=request.user,
            action='DELETE_INVOICE',
            details=f"Deleted unpaid invoice #{invoice_num} for student {student_name}"
        )

        messages.success(request, f"Invoice #{invoice_num} for {student_name} was deleted successfully.")
        return redirect('finance:invoices_list')

    return render(request, 'finance/invoice_confirm_delete.html', {
        'invoice': invoice,
        'has_payments': has_payments,
    })


@login_required
@accountant_required
def record_payment_view(request):
    invoice_id = request.GET.get('invoice_id')
    initial_data = {}
    selected_invoice = None

    if invoice_id:
        selected_invoice = get_object_or_404(Invoice, pk=invoice_id)
        initial_data['invoice'] = selected_invoice
        initial_data['amount'] = selected_invoice.balance

    if request.method == 'POST':
        form = PaymentRecordForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.save()

            AuditLog.objects.create(
                user=request.user,
                action='RECORD_PAYMENT',
                details=f"Recorded payment of {payment.amount} for {payment.invoice.student.full_name} (Receipt: {payment.receipt_number})"
            )

            messages.success(request, f"Payment of {payment.amount} recorded successfully. Receipt #{payment.receipt_number} generated.")
            return redirect('finance:receipt', pk=payment.pk)
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = PaymentRecordForm(initial=initial_data)

    return render(request, 'finance/record_payment.html', {
        'form': form,
        'selected_invoice': selected_invoice,
    })


@login_required
def receipt_view(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related(
            'invoice__student__current_class__class_level',
            'invoice__academic_session',
            'invoice__academic_term',
            'received_by'
        ),
        pk=pk
    )
    setting = SchoolSetting.load()

    return render(request, 'finance/receipt.html', {
        'payment': payment,
        'invoice': payment.invoice,
        'student': payment.invoice.student,
        'setting': setting,
    })


@login_required
@accountant_required
def generate_invoices_view(request):
    setting = SchoolSetting.load()
    initial_data = {
        'academic_session': setting.current_session,
        'academic_term': setting.current_term,
    }

    if request.method == 'POST':
        form = InvoiceGenerateForm(request.POST)
        if form.is_valid():
            session = form.cleaned_data['academic_session']
            term = form.cleaned_data['academic_term']
            class_section = form.cleaned_data.get('class_section')
            due_date = form.cleaned_data.get('due_date')

            students_qs = Student.objects.filter(status='ACTIVE')
            if class_section:
                students_qs = students_qs.filter(current_class=class_section)

            created_count = 0
            existing_count = 0

            for student in students_qs:
                if not student.current_class:
                    continue

                class_level = student.current_class.class_level
                # Calculate expected fees from fee structure
                structures = FeeStructure.objects.filter(
                    class_level=class_level,
                    academic_session=session,
                    academic_term=term
                )
                total_fees = structures.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

                invoice, created = Invoice.objects.get_or_create(
                    student=student,
                    academic_session=session,
                    academic_term=term,
                    defaults={
                        'total_amount': total_fees,
                        'due_date': due_date,
                    }
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

            AuditLog.objects.create(
                user=request.user,
                action='GENERATE_INVOICES',
                details=f"Generated {created_count} invoices for {session} {term}"
            )

            messages.success(request, f"Generated {created_count} new invoices. ({existing_count} already existed).")
            return redirect('finance:invoices_list')
    else:
        form = InvoiceGenerateForm(initial=initial_data)

    return render(request, 'finance/generate_invoices.html', {
        'form': form,
    })


@login_required
@accountant_required
def fee_structures_view(request):
    structures = FeeStructure.objects.select_related('fee_category', 'class_level', 'academic_session', 'academic_term').all()
    categories = FeeCategory.objects.all()

    form = FeeStructureForm()
    cat_form = FeeCategoryForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_structure':
            form = FeeStructureForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Fee structure configured successfully.")
                return redirect('finance:fee_structures')
            else:
                if '__all__' in form.errors:
                    messages.error(request, f"Fee structure already exists for this category, class, session, and term.")
                else:
                    messages.error(request, "Could not save fee structure. Please review the form fields.")
        elif action == 'add_category':
            cat_form = FeeCategoryForm(request.POST)
            if cat_form.is_valid():
                cat_form.save()
                messages.success(request, "Fee category added.")
                return redirect('finance:fee_structures')
            else:
                if 'name' in cat_form.errors:
                    messages.error(request, f"Cannot add category: {cat_form.errors['name'][0]}")
                else:
                    messages.error(request, "Could not add fee category.")

    return render(request, 'finance/fee_structures.html', {
        'structures': structures,
        'categories': categories,
        'form': form,
        'cat_form': cat_form,
    })
