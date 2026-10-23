from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum
from decimal import Decimal

from .models import SubjectResult, TermReportSummary
from .forms import TermReportRemarkForm
from apps.academics.models import ClassSection, Subject, SubjectAllocation, AcademicSession, AcademicTerm
from apps.students.models import Student
from apps.core.models import SchoolSetting, AuditLog
from apps.accounts.decorators import teacher_required


def compute_class_rankings(class_section, session, term):
    """
    Computes/updates student totals, averages, and class positions for the specified term.
    """
    students = Student.objects.filter(current_class=class_section, status='ACTIVE')
    student_scores = []

    for student in students:
        results = SubjectResult.objects.filter(
            student=student,
            class_section=class_section,
            academic_session=session,
            academic_term=term
        )
        if results.exists():
            total = results.aggregate(s=Sum('total'))['s'] or Decimal('0.00')
            avg = results.aggregate(a=Avg('total'))['a'] or Decimal('0.00')
            student_scores.append({
                'student': student,
                'total': total,
                'average': avg,
            })

    # Sort descending by total score
    student_scores.sort(key=lambda x: x['total'], reverse=True)
    total_students = len(student_scores)

    for rank, item in enumerate(student_scores, start=1):
        summary, _ = TermReportSummary.objects.get_or_create(
            student=item['student'],
            academic_session=session,
            academic_term=term,
            defaults={'class_section': class_section}
        )
        summary.class_section = class_section
        summary.total_score = item['total']
        summary.average_score = round(item['average'], 2)
        summary.position = rank
        summary.total_students_in_class = total_students
        summary.save()


@login_required
@teacher_required
def score_sheet_select_view(request):
    user = request.user
    setting = SchoolSetting.load()
    current_session = setting.current_session
    current_term = setting.current_term

    if user.is_principal:
        allocations = SubjectAllocation.objects.select_related(
            'teacher', 'subject', 'class_section__class_level', 'academic_session'
        ).all()
        classes = ClassSection.objects.select_related('class_level').all()
        subjects = Subject.objects.all()
    else:
        allocations = SubjectAllocation.objects.filter(
            teacher=user
        ).select_related('subject', 'class_section__class_level', 'academic_session')
        classes = ClassSection.objects.filter(id__in=allocations.values_list('class_section_id', flat=True))
        subjects = Subject.objects.filter(id__in=allocations.values_list('subject_id', flat=True))

    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()

    return render(request, 'results/score_sheet_select.html', {
        'allocations': allocations,
        'classes': classes,
        'subjects': subjects,
        'sessions': sessions,
        'terms': terms,
        'current_session': current_session,
        'current_term': current_term,
    })


@login_required
@teacher_required
def score_entry_sheet_view(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    session_id = request.GET.get('session_id')
    term_id = request.GET.get('term_id')

    setting = SchoolSetting.load()
    session = AcademicSession.objects.filter(id=session_id).first() if session_id else setting.current_session
    term = AcademicTerm.objects.filter(id=term_id).first() if term_id else setting.current_term

    if not class_id or not subject_id or not session or not term:
        messages.error(request, "Please select Class, Subject, Session, and Term to enter scores.")
        return redirect('results:select')

    class_section = get_object_or_404(ClassSection.objects.select_related('class_level'), id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)

    # Permission check: must be assigned teacher or principal/admin
    if not request.user.is_principal:
        is_allocated = SubjectAllocation.objects.filter(
            teacher=request.user,
            subject=subject,
            class_section=class_section
        ).exists()
        is_class_teacher = (class_section.class_teacher == request.user)
        if not (is_allocated or is_class_teacher):
            messages.error(request, "You are not assigned to record scores for this subject in this class.")
            return redirect('results:select')

    students = Student.objects.filter(current_class=class_section, status='ACTIVE').order_by('last_name', 'first_name')

    # Fetch existing results
    existing_results = {
        res.student_id: res for res in SubjectResult.objects.filter(
            class_section=class_section,
            subject=subject,
            academic_session=session,
            academic_term=term
        )
    }

    if request.method == 'POST':
        saved_count = 0
        for student in students:
            ca1_val = request.POST.get(f'ca1_{student.id}', '0').strip() or '0'
            ca2_val = request.POST.get(f'ca2_{student.id}', '0').strip() or '0'
            ca3_val = request.POST.get(f'ca3_{student.id}', '0').strip() or '0'
            exam_val = request.POST.get(f'exam_{student.id}', '0').strip() or '0'

            try:
                ca1 = Decimal(ca1_val)
                ca2 = Decimal(ca2_val)
                ca3 = Decimal(ca3_val)
                exam = Decimal(exam_val)
            except Exception:
                continue

            result_obj, created = SubjectResult.objects.get_or_create(
                student=student,
                subject=subject,
                academic_session=session,
                academic_term=term,
                defaults={
                    'class_section': class_section,
                    'teacher': request.user,
                }
            )
            result_obj.ca1 = ca1
            result_obj.ca2 = ca2
            result_obj.ca3 = ca3
            result_obj.exam = exam
            result_obj.class_section = class_section
            result_obj.teacher = request.user
            result_obj.save()
            saved_count += 1

        # Recompute rankings
        compute_class_rankings(class_section, session, term)

        AuditLog.objects.create(
            user=request.user,
            action='UPLOAD_SCORES',
            details=f"Uploaded {saved_count} scores for {subject.name} in {class_section.display_name} ({term})"
        )

        messages.success(request, f"Successfully saved scores for {saved_count} students in {subject.name}.")
        return redirect(f"{request.path}?class_id={class_id}&subject_id={subject_id}&session_id={session.id}&term_id={term.id}")

    # Build student row list for template
    student_rows = []
    for s in students:
        res = existing_results.get(s.id)
        student_rows.append({
            'student': s,
            'result': res,
            'ca1': res.ca1 if res else '0.00',
            'ca2': res.ca2 if res else '0.00',
            'ca3': res.ca3 if res else '0.00',
            'exam': res.exam if res else '0.00',
            'total': res.total if res else '0.00',
            'grade': res.grade if res else '-',
            'remark': res.remark if res else '-',
        })

    return render(request, 'results/score_entry_sheet.html', {
        'class_section': class_section,
        'subject': subject,
        'session': session,
        'term': term,
        'student_rows': student_rows,
        'setting': setting,
    })


@login_required
def class_broadsheet_view(request, class_id):
    class_section = get_object_or_404(ClassSection.objects.select_related('class_level'), id=class_id)
    setting = SchoolSetting.load()

    session_id = request.GET.get('session_id')
    term_id = request.GET.get('term_id')

    session = AcademicSession.objects.filter(id=session_id).first() if session_id else setting.current_session
    term = AcademicTerm.objects.filter(id=term_id).first() if term_id else setting.current_term

    if request.GET.get('recompute') == '1':
        compute_class_rankings(class_section, session, term)
        messages.success(request, "Class rankings and summaries recomputed successfully.")
        return redirect(f"{request.path}?session_id={session.id}&term_id={term.id}")

    students = Student.objects.filter(current_class=class_section, status='ACTIVE').order_by('last_name', 'first_name')
    subjects = Subject.objects.filter(results__class_section=class_section, results__academic_session=session, results__academic_term=term).distinct()

    # Pre-fetch all results for fast matrix building
    results_map = {}
    for r in SubjectResult.objects.filter(class_section=class_section, academic_session=session, academic_term=term):
        results_map[(r.student_id, r.subject_id)] = r

    summaries = {
        s.student_id: s for s in TermReportSummary.objects.filter(class_section=class_section, academic_session=session, academic_term=term)
    }

    broadsheet_data = []
    for st in students:
        row_subjects = []
        for sb in subjects:
            res = results_map.get((st.id, sb.id))
            row_subjects.append(res.total if res else '-')
        sm = summaries.get(st.id)
        broadsheet_data.append({
            'student': st,
            'subjects': row_subjects,
            'total': sm.total_score if sm else 0,
            'average': sm.average_score if sm else 0,
            'position': sm.position if sm else '-',
        })

    # Sort rows by position or average
    broadsheet_data.sort(key=lambda x: (x['position'] if isinstance(x['position'], int) else 999))

    return render(request, 'results/class_broadsheet.html', {
        'class_section': class_section,
        'session': session,
        'term': term,
        'subjects': subjects,
        'broadsheet_data': broadsheet_data,
        'sessions': AcademicSession.objects.all(),
        'terms': AcademicTerm.objects.all(),
    })


@login_required
def student_report_card_view(request, student_id):
    student = get_object_or_404(Student.objects.select_related('current_class__class_level'), id=student_id)
    setting = SchoolSetting.load()

    session_id = request.GET.get('session_id')
    term_id = request.GET.get('term_id')

    session = AcademicSession.objects.filter(id=session_id).first() if session_id else setting.current_session
    term = AcademicTerm.objects.filter(id=term_id).first() if term_id else setting.current_term

    results = SubjectResult.objects.filter(
        student=student,
        academic_session=session,
        academic_term=term
    ).select_related('subject', 'teacher').order_by('subject__name')

    summary, _ = TermReportSummary.objects.get_or_create(
        student=student,
        academic_session=session,
        academic_term=term,
        defaults={'class_section': student.current_class}
    )

    # Compute if not already computed
    if results.exists() and (summary.total_score == 0 or not summary.position):
        compute_class_rankings(student.current_class, session, term)
        summary.refresh_from_db()

    # Remark form for class teacher / principal
    if request.method == 'POST' and (request.user.is_principal or request.user == student.current_class.class_teacher):
        remark_form = TermReportRemarkForm(request.POST, instance=summary)
        if remark_form.is_valid():
            remark_form.save()
            messages.success(request, "Report card remarks and attendance updated.")
            return redirect(f"{request.path}?session_id={session.id}&term_id={term.id}")
    else:
        remark_form = TermReportRemarkForm(instance=summary)

    can_edit_remarks = request.user.is_principal or (student.current_class and student.current_class.class_teacher == request.user)

    return render(request, 'results/student_report_card.html', {
        'student': student,
        'session': session,
        'term': term,
        'results': results,
        'summary': summary,
        'setting': setting,
        'remark_form': remark_form,
        'can_edit_remarks': can_edit_remarks,
        'sessions': AcademicSession.objects.all(),
        'terms': AcademicTerm.objects.all(),
    })
