from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date
from decimal import Decimal

from apps.core.models import SchoolSetting, AuditLog
from apps.academics.models import AcademicSession, AcademicTerm, ClassLevel, ClassSection, Subject, SubjectAllocation
from apps.students.models import Student
from apps.results.models import SubjectResult, TermReportSummary
from apps.results.views import compute_class_rankings
from apps.finance.models import FeeCategory, FeeStructure, Invoice, Payment

User = get_user_model()


class SchoolManagementSystemTestCase(TestCase):
    def setUp(self):
        # 1. School Setting
        self.setting = SchoolSetting.load()
        self.setting.school_name = "Apex Test Secondary School"
        self.setting.save()

        # 2. Academic Session and Term
        self.session = AcademicSession.objects.create(name="2025/2026", is_current=True)
        self.term = AcademicTerm.objects.create(session=self.session, term_type=AcademicTerm.TermChoices.FIRST, is_current=True)
        self.setting.current_session = self.session
        self.setting.current_term = self.term
        self.setting.save()

        # 3. Staff Users with Roles
        self.principal = User.objects.create_user(
            username='principal_test',
            password='password123',
            role=User.Role.PRINCIPAL,
            first_name='Head',
            last_name='Principal'
        )
        self.teacher = User.objects.create_user(
            username='teacher_test',
            password='password123',
            role=User.Role.TEACHER,
            first_name='John',
            last_name='Teacher'
        )
        self.accountant = User.objects.create_user(
            username='accountant_test',
            password='password123',
            role=User.Role.ACCOUNTANT,
            first_name='Mary',
            last_name='Accountant'
        )

        # 4. Class and Subject
        self.level = ClassLevel.objects.create(name="JSS 1", order=1)
        self.class_section = ClassSection.objects.create(class_level=self.level, name="A", class_teacher=self.teacher)
        self.subject = Subject.objects.create(name="Mathematics", code="MTH")

        # Allocation
        self.allocation = SubjectAllocation.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            class_section=self.class_section,
            academic_session=self.session
        )

        # 5. Student
        self.student1 = Student.objects.create(
            admission_number="TEST/001",
            first_name="Alice",
            last_name="Johnson",
            gender="Female",
            date_of_birth=date(2013, 1, 1),
            admission_date=date(2025, 9, 1),
            current_class=self.class_section,
            guardian_name="Bob Johnson",
            guardian_phone="08012345678"
        )
        self.student2 = Student.objects.create(
            admission_number="TEST/002",
            first_name="David",
            last_name="Smith",
            gender="Male",
            date_of_birth=date(2013, 2, 2),
            admission_date=date(2025, 9, 1),
            current_class=self.class_section,
            guardian_name="Jane Smith",
            guardian_phone="08087654321"
        )

        self.client = Client()

    def test_school_settings_singleton(self):
        s1 = SchoolSetting.load()
        s2 = SchoolSetting.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(s1.school_name, "Apex Test Secondary School")

    def test_user_roles(self):
        self.assertTrue(self.principal.is_principal)
        self.assertFalse(self.principal.is_teacher)
        self.assertTrue(self.teacher.is_teacher)
        self.assertTrue(self.accountant.is_accountant)

    def test_score_calculation_and_grading(self):
        # Alice: CA1=14, CA2=14, CA3=10, Exam=52 -> Total = 90 -> Grade A1, Remark Excellent
        res1 = SubjectResult.objects.create(
            student=self.student1,
            subject=self.subject,
            class_section=self.class_section,
            academic_session=self.session,
            academic_term=self.term,
            teacher=self.teacher,
            ca1=Decimal('14.00'),
            ca2=Decimal('14.00'),
            ca3=Decimal('10.00'),
            exam=Decimal('52.00')
        )
        self.assertEqual(res1.total, Decimal('90.00'))
        self.assertEqual(res1.grade, 'A1')
        self.assertEqual(res1.remark, 'Excellent')

        # David: CA1=10, CA2=10, CA3=5, Exam=35 -> Total = 60 -> Grade C4, Remark Credit
        res2 = SubjectResult.objects.create(
            student=self.student2,
            subject=self.subject,
            class_section=self.class_section,
            academic_session=self.session,
            academic_term=self.term,
            teacher=self.teacher,
            ca1=Decimal('10.00'),
            ca2=Decimal('10.00'),
            ca3=Decimal('5.00'),
            exam=Decimal('35.00')
        )
        self.assertEqual(res2.total, Decimal('60.00'))
        self.assertEqual(res2.grade, 'C4')

        # Compute Rankings
        compute_class_rankings(self.class_section, self.session, self.term)
        summary1 = TermReportSummary.objects.get(student=self.student1, academic_term=self.term)
        summary2 = TermReportSummary.objects.get(student=self.student2, academic_term=self.term)

        self.assertEqual(summary1.position, 1)
        self.assertEqual(summary2.position, 2)
        self.assertEqual(summary1.total_students_in_class, 2)

    def test_finance_invoice_and_payment_recalculation(self):
        invoice = Invoice.objects.create(
            student=self.student1,
            academic_session=self.session,
            academic_term=self.term,
            total_amount=Decimal('100000.00')
        )
        self.assertEqual(invoice.balance, Decimal('100000.00'))
        self.assertEqual(invoice.status, Invoice.StatusChoices.UNPAID)

        # Make part payment
        payment1 = Payment.objects.create(
            invoice=invoice,
            amount=Decimal('60000.00'),
            payment_method=Payment.MethodChoices.BANK_TRANSFER,
            received_by=self.accountant
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal('60000.00'))
        self.assertEqual(invoice.balance, Decimal('40000.00'))
        self.assertEqual(invoice.status, Invoice.StatusChoices.PARTIAL)

        # Make remaining payment
        payment2 = Payment.objects.create(
            invoice=invoice,
            amount=Decimal('40000.00'),
            payment_method=Payment.MethodChoices.CASH,
            received_by=self.accountant
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal('100000.00'))
        self.assertEqual(invoice.balance, Decimal('0.00'))
        self.assertEqual(invoice.status, Invoice.StatusChoices.PAID)

    def test_login_and_dashboard_access(self):
        login_success = self.client.login(username='principal_test', password='password123')
        self.assertTrue(login_success)
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apex Test Secondary School")

    def test_duplicate_session_error_handling(self):
        self.client.login(username='principal_test', password='password123')
        # Try to add "2025/2026" again
        response = self.client.post(reverse('academics:calendar'), {
            'action': 'add_session',
            'name': '2025/2026',
            'start_date': '2025-09-01',
            'end_date': '2026-07-20',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(AcademicSession.objects.filter(name='2025/2026').count(), 1)

    def test_change_active_term(self):
        self.client.login(username='principal_test', password='password123')
        # Create second term
        term2 = AcademicTerm.objects.create(
            session=self.session,
            term_type=AcademicTerm.TermChoices.SECOND,
            is_current=False
        )
        response = self.client.post(reverse('academics:calendar'), {
            'action': 'set_current_term',
            'term_id': term2.id,
        })
        self.assertEqual(response.status_code, 302)
        term2.refresh_from_db()
        self.term.refresh_from_db()
        self.assertTrue(term2.is_current)
        self.assertFalse(self.term.is_current)

        setting = SchoolSetting.load()
        self.assertEqual(setting.current_term, term2)

    def test_delete_unpaid_invoice(self):
        self.client.login(username='accountant_test', password='password123')
        unpaid_invoice = Invoice.objects.create(
            student=self.student2,
            academic_session=self.session,
            academic_term=self.term,
            total_amount=Decimal('45000.00')
        )
        inv_id = unpaid_invoice.id
        inv_num = unpaid_invoice.invoice_number

        # Post delete request
        response = self.client.post(reverse('finance:invoice_delete', kwargs={'pk': inv_id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Invoice.objects.filter(id=inv_id).exists())
        self.assertTrue(AuditLog.objects.filter(action='DELETE_INVOICE', details__icontains=inv_num).exists())

    def test_delete_invoice_with_payments_blocked(self):
        self.client.login(username='accountant_test', password='password123')
        paid_invoice = Invoice.objects.create(
            student=self.student1,
            academic_session=self.session,
            academic_term=self.term,
            total_amount=Decimal('50000.00')
        )
        Payment.objects.create(
            invoice=paid_invoice,
            amount=Decimal('20000.00'),
            payment_method=Payment.MethodChoices.CASH,
            received_by=self.accountant
        )
        paid_invoice.refresh_from_db()
        self.assertEqual(paid_invoice.amount_paid, Decimal('20000.00'))

        # Post delete request should be refused
        response = self.client.post(reverse('finance:invoice_delete', kwargs={'pk': paid_invoice.pk}))
        self.assertEqual(response.status_code, 302)
        # Invoice MUST still exist!
        self.assertTrue(Invoice.objects.filter(id=paid_invoice.id).exists())

    def test_bulk_student_promotion_and_repeat(self):
        self.client.login(username='principal_test', password='password123')
        level2 = ClassLevel.objects.create(name="JSS 2", order=2)
        target_section = ClassSection.objects.create(class_level=level2, name="A")

        # Student 1 -> PROMOTE to JSS 2A
        # Student 2 -> REPEAT in JSS 1A
        response = self.client.post(reverse('students:promotion'), {
            'source_class_id': self.class_section.id,
            'selected_students': [self.student1.id, self.student2.id],
            'decision_' + str(self.student1.id): 'PROMOTE',
            'target_class_' + str(self.student1.id): target_section.id,
            'decision_' + str(self.student2.id): 'REPEAT',
            'target_class_' + str(self.student2.id): self.class_section.id,
        })
        self.assertEqual(response.status_code, 302)

        self.student1.refresh_from_db()
        self.student2.refresh_from_db()

        self.assertEqual(self.student1.current_class, target_section)
        self.assertEqual(self.student2.current_class, self.class_section)
        self.assertTrue(AuditLog.objects.filter(action='BULK_PROMOTION').exists())

    def test_student_list_pagination(self):
        self.client.login(username='principal_test', password='password123')
        # Create additional test students to test pagination
        for i in range(15):
            Student.objects.create(
                admission_number=f"TEST/PAG/{i}",
                first_name=f"Student{i}",
                last_name="Test",
                gender="Male",
                date_of_birth=date(2013, 1, 1),
                current_class=self.class_section,
                guardian_name="Test Guardian",
                guardian_phone="08000000000"
            )

        # GET with page_size=10
        response = self.client.get(reverse('students:student_list'), {'page_size': '10', 'page': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.per_page, 10)
        self.assertTrue(page_obj.has_other_pages())
        self.assertTrue(page_obj.has_next())
        self.assertEqual(page_obj.number, 1)

        # GET page 2
        response_page2 = self.client.get(reverse('students:student_list'), {'page_size': '10', 'page': '2'})
        self.assertEqual(response_page2.status_code, 200)
        page_obj2 = response_page2.context['page_obj']
        self.assertEqual(page_obj2.number, 2)
        self.assertTrue(page_obj2.has_previous())

    def test_class_edit_view_assign_teacher_to_unassigned_class(self):
        self.client.login(username='principal_test', password='password123')
        # Create unassigned class
        unassigned_class = ClassSection.objects.create(
            class_level=self.level,
            name="C",
            class_teacher=None
        )
        self.assertIsNone(unassigned_class.class_teacher)

        # GET class detail shows unassigned
        detail_res = self.client.get(reverse('academics:class_detail', kwargs={'pk': unassigned_class.pk}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Unassigned")
        self.assertContains(detail_res, reverse('academics:class_edit', kwargs={'pk': unassigned_class.pk}))

        # GET class edit form
        edit_get_res = self.client.get(reverse('academics:class_edit', kwargs={'pk': unassigned_class.pk}))
        self.assertEqual(edit_get_res.status_code, 200)

        # POST update assigning teacher
        post_res = self.client.post(reverse('academics:class_edit', kwargs={'pk': unassigned_class.pk}), {
            'class_level': self.level.id,
            'name': 'C',
            'class_teacher': self.teacher.id
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertRedirects(post_res, reverse('academics:class_detail', kwargs={'pk': unassigned_class.pk}))

        unassigned_class.refresh_from_db()
        self.assertEqual(unassigned_class.class_teacher, self.teacher)
        self.assertTrue(AuditLog.objects.filter(action='UPDATE_CLASS').exists())

    def test_class_edit_permission_guard(self):
        # Teacher without principal privileges cannot edit classes
        self.client.login(username='teacher_test', password='password123')
        response = self.client.get(reverse('academics:class_edit', kwargs={'pk': self.class_section.pk}))
        self.assertEqual(response.status_code, 302)

