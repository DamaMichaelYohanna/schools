from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import SchoolSetting, AuditLog
from .forms import SchoolSettingForm
from apps.accounts.decorators import principal_required
from apps.students.models import Student
from apps.academics.models import ClassSection, Subject, SubjectAllocation, AcademicSession, AcademicTerm
from apps.finance.models import Invoice, Payment
from apps.results.models import SubjectResult

User = get_user_model()


@login_required
def dashboard_view(request):
    user = request.user
    setting = SchoolSetting.load()
    context = {
        'setting': setting,
        'user': user,
    }

    if user.is_principal:
        # Principal / Admin Metrics
        context['total_students'] = Student.objects.filter(status='ACTIVE').count()
        context['total_staff'] = User.objects.filter(is_active_staff=True).count()
        context['total_classes'] = ClassSection.objects.count()
        context['total_subjects'] = Subject.objects.count()

        # Financial Metrics
        fin_stats = Invoice.objects.aggregate(
            total_invoiced=Sum('total_amount'),
            total_paid=Sum('amount_paid'),
            total_balance=Sum('balance')
        )
        context['total_invoiced'] = fin_stats['total_invoiced'] or Decimal('0.00')
        context['total_collected'] = fin_stats['total_paid'] or Decimal('0.00')
        context['total_outstanding'] = fin_stats['total_balance'] or Decimal('0.00')

        context['recent_payments'] = Payment.objects.select_related('invoice__student', 'received_by')[:5]
        context['recent_students'] = Student.objects.select_related('current_class')[:5]
        context['recent_audit_logs'] = AuditLog.objects.select_related('user')[:7]

    elif user.is_teacher:
        # Teacher Metrics
        allocations = SubjectAllocation.objects.filter(
            teacher=user
        ).select_related('subject', 'class_section', 'academic_session')
        
        context['my_allocations'] = allocations
        context['my_managed_classes'] = ClassSection.objects.filter(class_teacher=user)
        
        # Count distinct students across allocated classes
        class_ids = allocations.values_list('class_section_id', flat=True).distinct()
        context['my_students_count'] = Student.objects.filter(
            current_class_id__in=class_ids,
            status='ACTIVE'
        ).count()
        context['uploaded_scores_count'] = SubjectResult.objects.filter(teacher=user).count()

    elif user.is_accountant:
        # Accountant Metrics
        fin_stats = Invoice.objects.aggregate(
            total_invoiced=Sum('total_amount'),
            total_paid=Sum('amount_paid'),
            total_balance=Sum('balance')
        )
        context['total_invoiced'] = fin_stats['total_invoiced'] or Decimal('0.00')
        context['total_collected'] = fin_stats['total_paid'] or Decimal('0.00')
        context['total_outstanding'] = fin_stats['total_balance'] or Decimal('0.00')

        context['unpaid_invoices_count'] = Invoice.objects.filter(status__in=['UNPAID', 'PARTIAL']).count()
        context['recent_payments'] = Payment.objects.select_related('invoice__student', 'received_by')[:8]
        context['unpaid_invoices'] = Invoice.objects.filter(
            status__in=['UNPAID', 'PARTIAL']
        ).select_related('student', 'academic_term')[:6]

    return render(request, 'core/dashboard.html', context)


@login_required
@principal_required
def school_settings_view(request):
    setting = SchoolSetting.load()

    if request.method == 'POST':
        form = SchoolSettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE_SETTINGS',
                details=f"Updated school branding and parameters ({setting.school_name})"
            )
            messages.success(request, "School settings, branding, and academic configuration updated successfully!")
            return redirect('core:settings')
        else:
            messages.error(request, "There was an error saving school settings. Please check the fields.")
    else:
        form = SchoolSettingForm(instance=setting)

    return render(request, 'core/school_settings.html', {
        'form': form,
        'setting': setting,
    })


@login_required
@principal_required
def audit_logs_view(request):
    logs = AuditLog.objects.select_related('user').all()[:100]
    return render(request, 'core/audit_logs.html', {'logs': logs})
