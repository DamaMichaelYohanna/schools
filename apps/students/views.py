from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.urls import reverse

from .models import Student
from .forms import StudentForm
from apps.academics.models import ClassSection, ClassLevel, AcademicSession, AcademicTerm
from apps.accounts.decorators import principal_required
from apps.core.models import AuditLog, SchoolSetting
from apps.results.models import TermReportSummary


@login_required
def student_list_view(request):
    query = request.GET.get('q', '').strip()
    class_id = request.GET.get('class_id', '')
    status = request.GET.get('status', 'ACTIVE')

    students = Student.objects.select_related('current_class__class_level').all()

    if status:
        students = students.filter(status=status)

    if class_id:
        students = students.filter(current_class_id=class_id)

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(other_names__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(guardian_name__icontains=query) |
            Q(guardian_phone__icontains=query)
        )

    classes = ClassSection.objects.select_related('class_level').order_by('class_level__order', 'name')

    paginator = Paginator(students, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/student_list.html', {
        'page_obj': page_obj,
        'classes': classes,
        'selected_class': class_id,
        'selected_status': status,
        'query': query,
        'total_count': students.count(),
    })


@login_required
def student_create_view(request):
    if not (request.user.is_principal or request.user.role in ['ADMIN', 'TEACHER']):
        messages.error(request, "Access denied.")
        return redirect('students:student_list')

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_STUDENT',
                details=f"Registered student {student.full_name} ({student.admission_number})"
            )
            messages.success(request, f"Student {student.full_name} registered successfully with Admission No: {student.admission_number}")
            return redirect('students:student_detail', pk=student.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = StudentForm()

    return render(request, 'students/student_form.html', {
        'form': form,
        'title': 'New Student Admission & Record',
        'button_text': 'Enroll Student',
    })


@login_required
def student_detail_view(request, pk):
    student = get_object_or_404(Student.objects.select_related('current_class__class_level'), pk=pk)
    
    # Academic Results History
    reports = student.term_reports.select_related('academic_session', 'academic_term', 'class_section').order_by('-academic_session__name', '-academic_term__term_type')
    
    # Subject Results
    recent_results = student.subject_results.select_related('subject', 'academic_session', 'academic_term').order_by('-academic_session__name', 'subject__name')[:15]
    
    # Financial Invoices
    invoices = student.invoices.select_related('academic_session', 'academic_term').prefetch_related('payments').order_by('-created_at')

    return render(request, 'students/student_detail.html', {
        'student': student,
        'reports': reports,
        'recent_results': recent_results,
        'invoices': invoices,
    })


@login_required
def student_edit_view(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE_STUDENT',
                details=f"Updated records for {student.full_name} ({student.admission_number})"
            )
            messages.success(request, f"Record for {student.full_name} updated successfully.")
            return redirect('students:student_detail', pk=student.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {
        'form': form,
        'student': student,
        'title': f'Edit Student Record: {student.full_name}',
        'button_text': 'Save Changes',
    })


@login_required
@principal_required
def student_promotion_view(request):
    classes = ClassSection.objects.select_related('class_level').order_by('class_level__order', 'name')
    setting = SchoolSetting.load()

    class_id = request.GET.get('class_id') or request.POST.get('source_class_id')
    selected_class = None
    next_level = None
    recommended_target_class = None
    is_final_level = False
    students_data = []

    if class_id:
        selected_class = get_object_or_404(ClassSection.objects.select_related('class_level'), pk=class_id)

        # Determine next class level in sequence
        next_level = ClassLevel.objects.filter(order__gt=selected_class.class_level.order).order_by('order').first()
        if next_level:
            recommended_target_class = ClassSection.objects.filter(
                class_level=next_level,
                name__iexact=selected_class.name
            ).first() or ClassSection.objects.filter(class_level=next_level).first()
        else:
            is_final_level = True

        # Handle POST: Execute promotions
        if request.method == 'POST':
            student_ids = request.POST.getlist('selected_students')
            if not student_ids:
                messages.warning(request, "No students were selected for promotion processing.")
                return redirect(f"{reverse('students:promotion')}?class_id={selected_class.id}")

            promoted_count = 0
            repeated_count = 0
            graduated_count = 0
            withdrawn_count = 0

            with transaction.atomic():
                for s_id in student_ids:
                    student = get_object_or_404(Student, id=s_id, current_class=selected_class)
                    decision = request.POST.get(f'decision_{s_id}')
                    target_class_id = request.POST.get(f'target_class_{s_id}') or request.POST.get('bulk_target_class_id')

                    if decision == 'PROMOTE':
                        if target_class_id:
                            target_sec = get_object_or_404(ClassSection, id=target_class_id)
                            student.current_class = target_sec
                            student.save(update_fields=['current_class', 'updated_at'])
                            promoted_count += 1
                        elif is_final_level:
                            student.status = Student.StatusChoices.GRADUATED
                            student.current_class = None
                            student.save(update_fields=['status', 'current_class', 'updated_at'])
                            graduated_count += 1
                    elif decision == 'REPEAT':
                        repeat_target_id = request.POST.get(f'target_class_{s_id}') or selected_class.id
                        repeat_sec = get_object_or_404(ClassSection, id=repeat_target_id)
                        student.current_class = repeat_sec
                        student.save(update_fields=['current_class', 'updated_at'])
                        repeated_count += 1
                    elif decision == 'GRADUATE':
                        student.status = Student.StatusChoices.GRADUATED
                        student.current_class = None
                        student.save(update_fields=['status', 'current_class', 'updated_at'])
                        graduated_count += 1
                    elif decision == 'WITHDRAW':
                        student.status = Student.StatusChoices.WITHDRAWN
                        student.current_class = None
                        student.save(update_fields=['status', 'current_class', 'updated_at'])
                        withdrawn_count += 1

            AuditLog.objects.create(
                user=request.user,
                action='BULK_PROMOTION',
                details=(
                    f"Processed bulk rollover for {selected_class.display_name}: "
                    f"{promoted_count} promoted, {repeated_count} repeated, "
                    f"{graduated_count} graduated, {withdrawn_count} withdrawn."
                )
            )

            messages.success(
                request,
                f"Promotion completed for {selected_class.display_name}: {promoted_count} promoted, "
                f"{repeated_count} repeated, {graduated_count} graduated, {withdrawn_count} withdrawn."
            )
            return redirect(f"{reverse('students:promotion')}?class_id={selected_class.id}")

        # GET: Fetch active students and attach latest reports
        students_qs = Student.objects.filter(current_class=selected_class, status='ACTIVE').order_by('last_name', 'first_name')
        
        reports = TermReportSummary.objects.filter(
            student__in=students_qs,
            class_section=selected_class
        ).order_by('-academic_session__name', '-academic_term__term_type')

        student_reports_map = {}
        for r in reports:
            if r.student_id not in student_reports_map:
                student_reports_map[r.student_id] = r

        for s in students_qs:
            report = student_reports_map.get(s.id)
            avg = float(report.average_score) if report and report.average_score else None
            default_decision = 'PROMOTE'
            if is_final_level:
                default_decision = 'GRADUATE' if (avg is None or avg >= 50) else 'REPEAT'
            elif avg is not None and avg < 50:
                default_decision = 'REPEAT'

            students_data.append({
                'student': s,
                'report': report,
                'average': avg,
                'position': report.position if report else None,
                'default_decision': default_decision,
            })

    return render(request, 'students/promotion.html', {
        'classes': classes,
        'selected_class': selected_class,
        'next_level': next_level,
        'recommended_target_class': recommended_target_class,
        'is_final_level': is_final_level,
        'students_data': students_data,
        'setting': setting,
    })
