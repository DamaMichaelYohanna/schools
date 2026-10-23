from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import ClassLevel, ClassSection, Subject, SubjectAllocation, AcademicSession, AcademicTerm
from .forms import SubjectAllocationForm, SubjectForm, ClassSectionForm, AcademicSessionForm, AcademicTermForm
from apps.accounts.decorators import principal_required
from apps.core.models import AuditLog, SchoolSetting


@login_required
def class_list_view(request):
    classes = ClassSection.objects.select_related('class_level', 'class_teacher').annotate(
        active_students=Count('students')
    ).order_by('class_level__order', 'name')
    
    levels = ClassLevel.objects.all().order_by('order')

    return render(request, 'academics/class_list.html', {
        'classes': classes,
        'levels': levels,
    })


@login_required
def class_detail_view(request, pk):
    cls = get_object_or_404(ClassSection.objects.select_related('class_level', 'class_teacher'), pk=pk)
    students = cls.students.filter(status='ACTIVE').order_by('last_name', 'first_name')
    allocations = cls.subject_allocations.select_related('subject', 'teacher', 'academic_session').all()

    return render(request, 'academics/class_detail.html', {
        'cls': cls,
        'students': students,
        'allocations': allocations,
    })


@login_required
@principal_required
def class_create_view(request):
    if request.method == 'POST':
        form = ClassSectionForm(request.POST)
        if form.is_valid():
            new_cls = form.save()
            messages.success(request, f"Class arm '{new_cls.display_name}' created successfully.")
            return redirect('academics:class_list')
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = ClassSectionForm()

    return render(request, 'academics/form_generic.html', {
        'form': form,
        'title': 'Add Class Arm / Section',
        'button_text': 'Create Class',
        'back_url': 'academics:class_list',
    })


@login_required
def subject_list_view(request):
    subjects = Subject.objects.annotate(
        allocated_count=Count('allocations')
    ).order_by('name')

    if request.method == 'POST' and request.user.is_principal:
        form = SubjectForm(request.POST)
        if form.is_valid():
            sub = form.save()
            messages.success(request, f"Subject '{sub.name} ({sub.code})' added successfully.")
            return redirect('academics:subject_list')
        else:
            if 'name' in form.errors:
                messages.error(request, f"Cannot add subject: {form.errors['name'][0]}")
            elif 'code' in form.errors:
                messages.error(request, f"Cannot add subject: {form.errors['code'][0]}")
            else:
                messages.error(request, "Could not add subject. Please check the form fields.")
    else:
        form = SubjectForm()

    return render(request, 'academics/subject_list.html', {
        'subjects': subjects,
        'form': form,
    })


@login_required
def allocation_list_view(request):
    allocations = SubjectAllocation.objects.select_related(
        'teacher', 'subject', 'class_section__class_level', 'academic_session'
    ).order_by('class_section__class_level__order', 'class_section__name', 'subject__name')

    # Filter by teacher if teacher role
    if request.user.is_teacher and not request.user.is_principal:
        allocations = allocations.filter(teacher=request.user)

    return render(request, 'academics/allocation_list.html', {
        'allocations': allocations,
    })


@login_required
@principal_required
def allocation_create_view(request):
    setting = SchoolSetting.load()
    initial_data = {}
    if setting.current_session:
        initial_data['academic_session'] = setting.current_session

    if request.method == 'POST':
        form = SubjectAllocationForm(request.POST)
        if form.is_valid():
            alloc = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='ALLOCATE_SUBJECT',
                details=f"Assigned {alloc.subject.name} in {alloc.class_section.display_name} to {alloc.teacher.full_name}"
            )
            messages.success(request, f"Allocated {alloc.subject.name} to {alloc.teacher.full_name} for {alloc.class_section.display_name}.")
            return redirect('academics:allocation_list')
        else:
            messages.error(request, "Could not save allocation. It may already exist for this session.")
    else:
        form = SubjectAllocationForm(initial=initial_data)

    return render(request, 'academics/form_generic.html', {
        'form': form,
        'title': 'Assign Subject to Teacher',
        'button_text': 'Confirm Allocation',
        'back_url': 'academics:allocation_list',
    })


@login_required
@principal_required
def allocation_delete_view(request, pk):
    alloc = get_object_or_404(SubjectAllocation, pk=pk)
    if request.method == 'POST':
        name = str(alloc)
        alloc.delete()
        messages.success(request, f"Allocation '{name}' removed successfully.")
        return redirect('academics:allocation_list')

    return render(request, 'academics/confirm_delete.html', {
        'object': alloc,
        'title': 'Remove Subject Allocation',
        'cancel_url': 'academics:allocation_list',
    })


@login_required
@principal_required
def academic_calendar_view(request):
    sessions = AcademicSession.objects.prefetch_related('terms').order_by('-name')
    session_form = AcademicSessionForm()
    term_form = AcademicTermForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_session':
            session_form = AcademicSessionForm(request.POST)
            if session_form.is_valid():
                s = session_form.save()
                messages.success(request, f"Academic session '{s.name}' created.")
                return redirect('academics:calendar')
            else:
                if 'name' in session_form.errors:
                    messages.error(request, f"Cannot create session: {session_form.errors['name'][0]}")
                else:
                    messages.error(request, "Could not create academic session. Please review the form errors.")
        elif action == 'add_term':
            term_form = AcademicTermForm(request.POST)
            if term_form.is_valid():
                t = term_form.save()
                messages.success(request, f"Academic term '{t}' created.")
                return redirect('academics:calendar')
            else:
                if '__all__' in term_form.errors:
                    messages.error(request, f"Cannot create term: {term_form.errors['__all__'][0]}")
                elif 'term_type' in term_form.errors:
                    messages.error(request, f"Cannot create term: {term_form.errors['term_type'][0]}")
                else:
                    messages.error(request, "Could not create academic term. Please review the form errors.")
        elif action == 'set_current_term':
            term_id = request.POST.get('term_id')
            term = get_object_or_404(AcademicTerm.objects.select_related('session'), id=term_id)
            
            # Deactivate all other terms and activate this one
            AcademicTerm.objects.exclude(id=term.id).update(is_current=False)
            term.is_current = True
            term.save()

            # Ensure term's session is also current
            session = term.session
            AcademicSession.objects.exclude(id=session.id).update(is_current=False)
            session.is_current = True
            session.save()

            # Update SchoolSetting singleton so context processor updates everywhere
            setting = SchoolSetting.load()
            setting.current_session = session
            setting.current_term = term
            setting.save()

            AuditLog.objects.create(
                user=request.user,
                action='CHANGE_ACTIVE_TERM',
                details=f"Switched active academic term to {term.term_type} ({session.name})"
            )

            messages.success(request, f"Active term successfully changed to '{term.term_type}' ({session.name}).")
            return redirect('academics:calendar')

        elif action == 'set_current_session':
            session_id = request.POST.get('session_id')
            session = get_object_or_404(AcademicSession, id=session_id)
            AcademicSession.objects.exclude(id=session.id).update(is_current=False)
            session.is_current = True
            session.save()

            # Pick active term in this session, or default to 1st Term
            first_term = session.terms.filter(term_type=AcademicTerm.TermChoices.FIRST).first() or session.terms.first()
            if first_term:
                AcademicTerm.objects.exclude(id=first_term.id).update(is_current=False)
                first_term.is_current = True
                first_term.save()

            setting = SchoolSetting.load()
            setting.current_session = session
            if first_term:
                setting.current_term = first_term
            setting.save()

            AuditLog.objects.create(
                user=request.user,
                action='CHANGE_ACTIVE_SESSION',
                details=f"Switched active academic session to {session.name}"
            )

            messages.success(request, f"Active session successfully changed to '{session.name}'.")
            return redirect('academics:calendar')

    all_terms = AcademicTerm.objects.select_related('session').order_by('-session__name', 'term_type')

    return render(request, 'academics/calendar.html', {
        'sessions': sessions,
        'all_terms': all_terms,
        'session_form': session_form,
        'term_form': term_form,
    })
