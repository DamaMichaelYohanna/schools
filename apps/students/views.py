from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Student
from .forms import StudentForm
from apps.academics.models import ClassSection
from apps.accounts.decorators import principal_required
from apps.core.models import AuditLog


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
