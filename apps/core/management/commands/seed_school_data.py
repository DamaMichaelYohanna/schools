from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from decimal import Decimal

from apps.core.models import SchoolSetting, AuditLog
from apps.academics.models import AcademicSession, AcademicTerm, ClassLevel, ClassSection, Subject, SubjectAllocation
from apps.students.models import Student
from apps.results.models import SubjectResult, TermReportSummary
from apps.results.views import compute_class_rankings
from apps.finance.models import FeeCategory, FeeStructure, Invoice, Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds realistic secondary school demo data: Principal, Teachers, Accountant, Classes, Students, Scores, Fees.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Beginning secondary school data seeding..."))

        # 1. Academic Sessions and Terms
        session, _ = AcademicSession.objects.get_or_create(
            name='2025/2026',
            defaults={
                'start_date': date(2025, 9, 8),
                'end_date': date(2026, 7, 24),
                'is_current': True
            }
        )
        term1, _ = AcademicTerm.objects.get_or_create(
            session=session,
            term_type=AcademicTerm.TermChoices.FIRST,
            defaults={
                'start_date': date(2025, 9, 8),
                'end_date': date(2025, 12, 12),
                'is_current': True
            }
        )
        term2, _ = AcademicTerm.objects.get_or_create(
            session=session,
            term_type=AcademicTerm.TermChoices.SECOND,
            defaults={
                'start_date': date(2026, 1, 12),
                'end_date': date(2026, 4, 3),
                'is_current': False
            }
        )
        term3, _ = AcademicTerm.objects.get_or_create(
            session=session,
            term_type=AcademicTerm.TermChoices.THIRD,
            defaults={
                'start_date': date(2026, 4, 27),
                'end_date': date(2026, 7, 24),
                'is_current': False
            }
        )

        # 2. School Settings (DB Controlled Name & Branding)
        setting = SchoolSetting.load()
        setting.school_name = 'Apex Horizon International Secondary School'
        setting.school_motto = 'Knowledge, Character & Leadership for the Future'
        setting.email = 'admin@apexhorizon.edu.ng'
        setting.phone = '+234 803 555 0192 / +234 812 345 6789'
        setting.address = 'Plot 15 Academy Crescent, Victoria Island, Lagos'
        setting.current_session = session
        setting.current_term = term1
        setting.currency_symbol = '₦'
        setting.ca1_max = 15
        setting.ca2_max = 15
        setting.ca3_max = 10
        setting.exam_max = 60
        setting.save()

        # 3. Staff Users
        # Principal
        principal, _ = User.objects.get_or_create(
            username='principal',
            defaults={
                'first_name': 'Dr. Augustus',
                'last_name': 'Adeleke',
                'email': 'principal@apexhorizon.edu.ng',
                'role': User.Role.PRINCIPAL,
                'staff_id': 'STF-ADM-001',
                'phone_number': '+234 803 111 2233',
                'qualification': 'Ph.D Educational Administration, M.Ed',
                'date_employed': date(2018, 8, 1),
                'is_staff': True,
                'is_superuser': True,
            }
        )
        principal.set_password('password123')
        principal.save()

        # Math Teacher
        teacher_math, _ = User.objects.get_or_create(
            username='teacher_math',
            defaults={
                'first_name': 'Emmanuel',
                'last_name': 'Adeyemi',
                'email': 'e.adeyemi@apexhorizon.edu.ng',
                'role': User.Role.TEACHER,
                'staff_id': 'STF-TCH-002',
                'phone_number': '+234 805 222 3344',
                'qualification': 'B.Sc (Ed) Mathematics, Unilag',
                'date_employed': date(2021, 9, 1),
                'is_staff': True,
            }
        )
        teacher_math.set_password('password123')
        teacher_math.save()

        # English Teacher
        teacher_eng, _ = User.objects.get_or_create(
            username='teacher_eng',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Obi',
                'email': 's.obi@apexhorizon.edu.ng',
                'role': User.Role.TEACHER,
                'staff_id': 'STF-TCH-003',
                'phone_number': '+234 807 333 4455',
                'qualification': 'B.A (Ed) English Language, UNN',
                'date_employed': date(2022, 1, 10),
                'is_staff': True,
            }
        )
        teacher_eng.set_password('password123')
        teacher_eng.save()

        # Science Teacher
        teacher_sci, _ = User.objects.get_or_create(
            username='teacher_sci',
            defaults={
                'first_name': 'Dr. Michael',
                'last_name': 'Okon',
                'email': 'm.okon@apexhorizon.edu.ng',
                'role': User.Role.TEACHER,
                'staff_id': 'STF-TCH-004',
                'phone_number': '+234 809 444 5566',
                'qualification': 'Ph.D Physics, M.Sc Applied Geophysics',
                'date_employed': date(2020, 10, 15),
                'is_staff': True,
            }
        )
        teacher_sci.set_password('password123')
        teacher_sci.save()

        # Accountant / Bursar
        accountant, _ = User.objects.get_or_create(
            username='accountant',
            defaults={
                'first_name': 'Florence',
                'last_name': 'Bello',
                'email': 'bursar@apexhorizon.edu.ng',
                'role': User.Role.ACCOUNTANT,
                'staff_id': 'STF-ACC-005',
                'phone_number': '+234 802 888 9900',
                'qualification': 'B.Sc Accounting, ACA (ICAN)',
                'date_employed': date(2019, 5, 20),
                'is_staff': True,
            }
        )
        accountant.set_password('password123')
        accountant.save()

        # 4. Class Levels and Sections
        class_levels_data = [
            ('JSS 1', 1), ('JSS 2', 2), ('JSS 3', 3),
            ('SSS 1', 4), ('SSS 2', 5), ('SSS 3', 6),
        ]
        levels = {}
        for name, order in class_levels_data:
            lvl, _ = ClassLevel.objects.get_or_create(name=name, defaults={'order': order})
            levels[name] = lvl

        # Sections
        jss1a, _ = ClassSection.objects.get_or_create(class_level=levels['JSS 1'], name='A', defaults={'class_teacher': teacher_math})
        jss1b, _ = ClassSection.objects.get_or_create(class_level=levels['JSS 1'], name='B', defaults={'class_teacher': teacher_eng})
        jss2a, _ = ClassSection.objects.get_or_create(class_level=levels['JSS 2'], name='A', defaults={'class_teacher': teacher_math})
        sss1_sci, _ = ClassSection.objects.get_or_create(class_level=levels['SSS 1'], name='Science', defaults={'class_teacher': teacher_sci})
        sss1_art, _ = ClassSection.objects.get_or_create(class_level=levels['SSS 1'], name='Arts', defaults={'class_teacher': teacher_eng})
        sss2_sci, _ = ClassSection.objects.get_or_create(class_level=levels['SSS 2'], name='Science', defaults={'class_teacher': teacher_sci})

        # 5. Curriculum Subjects
        subjects_data = [
            ('Mathematics', 'MTH', False, 'Core secondary mathematics and numeracy'),
            ('English Language', 'ENG', False, 'Grammar, comprehension, and oral English'),
            ('Basic Science & Technology', 'BST', False, 'Foundational integrated science and technology'),
            ('Physics', 'PHY', False, 'Mechanics, optics, waves, and modern physics'),
            ('Chemistry', 'CHM', False, 'Inorganic, organic, and physical chemistry'),
            ('Biology', 'BIO', False, 'Living organisms, ecology, and physiology'),
            ('Civic Education', 'CVE', False, 'Democratic governance, human rights, and citizenship'),
            ('Economics', 'ECN', False, 'Principles of micro and macro economics'),
            ('Agricultural Science', 'AGR', True, 'Crop production and animal husbandry'),
            ('Further Mathematics', 'FMTH', True, 'Advanced pure and applied mathematics'),
        ]
        subjects = {}
        for name, code, is_elec, desc in subjects_data:
            sb, _ = Subject.objects.get_or_create(code=code, defaults={'name': name, 'is_elective': is_elec, 'description': desc})
            subjects[code] = sb

        # 6. Allocations
        allocations_to_create = [
            (teacher_math, subjects['MTH'], jss1a),
            (teacher_math, subjects['MTH'], jss2a),
            (teacher_math, subjects['MTH'], sss1_sci),
            (teacher_eng, subjects['ENG'], jss1a),
            (teacher_eng, subjects['ENG'], jss2a),
            (teacher_eng, subjects['ENG'], sss1_sci),
            (teacher_sci, subjects['BST'], jss1a),
            (teacher_sci, subjects['PHY'], sss1_sci),
            (teacher_sci, subjects['CHM'], sss1_sci),
        ]
        for t, s, c in allocations_to_create:
            SubjectAllocation.objects.get_or_create(
                teacher=t,
                subject=s,
                class_section=c,
                academic_session=session
            )

        # 7. Students Records
        sample_students = [
            ('SEC/2025/001', 'Chinedu', 'Okafor', 'David', 'Male', date(2013, 4, 15), jss1a, 'Chief Emeka Okafor', '+234 803 777 0001', 'emeka.okafor@gmail.com'),
            ('SEC/2025/002', 'Amina', 'Bello', 'Zainab', 'Female', date(2013, 8, 22), jss1a, 'Alhaji Usman Bello', '+234 802 777 0002', 'usman.bello@yahoo.com'),
            ('SEC/2025/003', 'Femi', 'Adeyinka', 'Joshua', 'Male', date(2013, 11, 5), jss1a, 'Barrister Tunde Adeyinka', '+234 805 777 0003', 'tunde.adeyinka@law.ng'),
            ('SEC/2025/004', 'Blessing', 'Eze', 'Chioma', 'Female', date(2013, 2, 19), jss1a, 'Mrs. Ngozi Eze', '+234 807 777 0004', 'ngozi.eze@gmail.com'),
            ('SEC/2025/005', 'Tari', 'Briggs', 'Godwin', 'Male', date(2013, 6, 30), jss1a, 'Captain Briggs Tari', '+234 809 777 0005', 'briggs.tari@marine.ng'),
            ('SEC/2025/006', 'Halima', 'Danjuma', 'Fatima', 'Female', date(2013, 9, 12), jss1a, 'Dr. Abdullahi Danjuma', '+234 812 777 0006', 'danjuma.a@health.gov.ng'),
            ('SEC/2025/007', 'Kelechi', 'Nwosu', 'Paul', 'Male', date(2013, 1, 28), jss1a, 'Mr. Innocent Nwosu', '+234 818 777 0007', 'innocent.nwosu@biz.ng'),
            ('SEC/2025/008', 'Damilola', 'Ogunleye', 'Grace', 'Female', date(2013, 7, 14), jss1a, 'Engr. Yemi Ogunleye', '+234 808 777 0008', 'yemi.ogunleye@shell.com'),
            
            # SSS 1 Science
            ('SEC/2023/101', 'Somtochukwu', 'Anyanwu', 'Francis', 'Male', date(2010, 3, 10), sss1_sci, 'Dr. Christopher Anyanwu', '+234 803 888 1111', 'chris.anyanwu@med.org'),
            ('SEC/2023/102', 'Zainab', 'Mohammed', 'Aisha', 'Female', date(2010, 6, 25), sss1_sci, 'Hon. Kabir Mohammed', '+234 802 888 2222', 'kabir.m@parliament.ng'),
            ('SEC/2023/103', 'Oluwaseun', 'Balogun', 'Samuel', 'Male', date(2010, 9, 18), sss1_sci, 'Prof. Kunle Balogun', '+234 805 888 3333', 'kunle.balogun@unilag.edu.ng'),
            ('SEC/2023/104', 'Nafisat', 'Suleiman', 'Maryam', 'Female', date(2010, 12, 4), sss1_sci, 'Hajiya Binta Suleiman', '+234 807 888 4444', 'binta.suleiman@trade.gov.ng'),
        ]

        created_students = []
        for adm, fn, ln, on, gen, dob, cls, g_name, g_phone, g_email in sample_students:
            st, _ = Student.objects.get_or_create(
                admission_number=adm,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'other_names': on,
                    'gender': gen,
                    'date_of_birth': dob,
                    'admission_date': date(2025, 9, 8) if '2025' in adm else date(2023, 9, 10),
                    'current_class': cls,
                    'blood_group': 'O+',
                    'genotype': 'AA',
                    'nationality': 'Nigerian',
                    'residential_address': 'Plot 22 Parkview Estate, Ikoyi, Lagos',
                    'guardian_name': g_name,
                    'guardian_relationship': 'Father' if 'Alhaji' in g_name or 'Chief' in g_name or 'Mr.' in g_name or 'Dr.' in g_name else 'Mother',
                    'guardian_phone': g_phone,
                    'guardian_email': g_email,
                    'guardian_address': 'Plot 22 Parkview Estate, Ikoyi, Lagos',
                    'status': Student.StatusChoices.ACTIVE,
                }
            )
            created_students.append(st)

        # 8. Sample Scores & Results for JSS 1A
        jss1a_students = [s for s in created_students if s.current_class == jss1a]
        
        # Predefined realistic continuous assessment & exam scores
        score_samples = {
            'SEC/2025/001': {'MTH': (14, 14, 9, 54), 'ENG': (13, 14, 9, 52), 'BST': (14, 15, 10, 56)}, # Top student ~ 90+
            'SEC/2025/002': {'MTH': (13, 14, 8, 50), 'ENG': (14, 14, 9, 55), 'BST': (13, 13, 8, 50)},  # ~ 85
            'SEC/2025/003': {'MTH': (12, 13, 8, 48), 'ENG': (12, 13, 8, 45), 'BST': (12, 12, 8, 46)},  # ~ 80
            'SEC/2025/004': {'MTH': (11, 12, 7, 44), 'ENG': (13, 13, 9, 50), 'BST': (12, 11, 8, 44)},  # ~ 75
            'SEC/2025/005': {'MTH': (10, 11, 7, 40), 'ENG': (11, 10, 7, 42), 'BST': (11, 11, 7, 42)},  # ~ 68
            'SEC/2025/006': {'MTH': (9, 10, 6, 36),  'ENG': (10, 11, 7, 38), 'BST': (10, 9, 6, 38)},   # ~ 60
            'SEC/2025/007': {'MTH': (8, 9, 6, 32),   'ENG': (9, 9, 6, 34),   'BST': (9, 8, 6, 33)},    # ~ 55
            'SEC/2025/008': {'MTH': (12, 13, 9, 51), 'ENG': (14, 15, 10, 54), 'BST': (13, 14, 9, 52)}, # ~ 87
        }

        for st in jss1a_students:
            scores = score_samples.get(st.admission_number, {})
            for code, (c1, c2, c3, ex) in scores.items():
                sb = subjects[code]
                t_user = teacher_math if code == 'MTH' else (teacher_eng if code == 'ENG' else teacher_sci)
                res, _ = SubjectResult.objects.get_or_create(
                    student=st,
                    subject=sb,
                    academic_session=session,
                    academic_term=term1,
                    defaults={
                        'class_section': jss1a,
                        'teacher': t_user,
                        'ca1': Decimal(str(c1)),
                        'ca2': Decimal(str(c2)),
                        'ca3': Decimal(str(c3)),
                        'exam': Decimal(str(ex)),
                    }
                )
                res.ca1 = Decimal(str(c1))
                res.ca2 = Decimal(str(c2))
                res.ca3 = Decimal(str(c3))
                res.exam = Decimal(str(ex))
                res.save()

        # Compute positions and terminal report summary
        compute_class_rankings(jss1a, session, term1)

        # Set specific pleasant remarks on the top student report card
        top_report = TermReportSummary.objects.filter(student__admission_number='SEC/2025/001', academic_term=term1).first()
        if top_report:
            top_report.days_present = 64
            top_report.total_school_days = 65
            top_report.teacher_remark = 'An exceptionally brilliant, diligent and well-behaved young scholar.'
            top_report.principal_remark = 'Outstanding performance! Congratulations on maintaining 1st position.'
            top_report.next_term_resumption = date(2026, 1, 12)
            top_report.save()

        # 9. Fee Categories & Structures
        tuition, _ = FeeCategory.objects.get_or_create(name='Tuition Fee', defaults={'description': 'Main term academic tuition'})
        dev_levy, _ = FeeCategory.objects.get_or_create(name='Development Levy', defaults={'description': 'Campus development and maintenance'})
        ict_fee, _ = FeeCategory.objects.get_or_create(name='ICT & Computer Lab Fee', defaults={'description': 'High-speed internet and digital lab'})
        pta_levy, _ = FeeCategory.objects.get_or_create(name='PTA Levy', defaults={'description': 'Parents Teachers Association term contribution'})

        # JSS 1 Fees
        FeeStructure.objects.get_or_create(fee_category=tuition, class_level=levels['JSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('150000.00')})
        FeeStructure.objects.get_or_create(fee_category=dev_levy, class_level=levels['JSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('30000.00')})
        FeeStructure.objects.get_or_create(fee_category=ict_fee, class_level=levels['JSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('20000.00')})
        FeeStructure.objects.get_or_create(fee_category=pta_levy, class_level=levels['JSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('10000.00')})

        # SSS 1 Fees
        FeeStructure.objects.get_or_create(fee_category=tuition, class_level=levels['SSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('180000.00')})
        FeeStructure.objects.get_or_create(fee_category=dev_levy, class_level=levels['SSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('35000.00')})
        FeeStructure.objects.get_or_create(fee_category=ict_fee, class_level=levels['SSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('25000.00')})
        FeeStructure.objects.get_or_create(fee_category=pta_levy, class_level=levels['SSS 1'], academic_session=session, academic_term=term1, defaults={'amount': Decimal('10000.00')})

        # 10. Invoices and Payments
        # Generate invoices for JSS 1A students (Total JSS 1 = 150k + 30k + 20k + 10k = 210,000)
        total_jss1_fee = Decimal('210000.00')
        for idx, st in enumerate(jss1a_students, start=1):
            inv, created = Invoice.objects.get_or_create(
                student=st,
                academic_session=session,
                academic_term=term1,
                defaults={
                    'invoice_number': f"INV-2025-J10{idx}",
                    'total_amount': total_jss1_fee,
                    'due_date': date(2025, 10, 15),
                }
            )

            # Record payments for some students
            if idx in [1, 2, 8]:
                # Fully paid
                if not inv.payments.exists():
                    Payment.objects.create(
                        receipt_number=f"RCP-2025-00{idx}",
                        invoice=inv,
                        amount=total_jss1_fee,
                        payment_method=Payment.MethodChoices.BANK_TRANSFER,
                        transaction_reference=f"TRF/GTB/99281{idx}",
                        payment_date=date(2025, 9, 15),
                        received_by=accountant,
                        remarks='Full term payment received via GTBank direct transfer'
                    )
            elif idx in [3, 4, 5]:
                # Partially paid (150k)
                if not inv.payments.exists():
                    Payment.objects.create(
                        receipt_number=f"RCP-2025-00{idx}",
                        invoice=inv,
                        amount=Decimal('150000.00'),
                        payment_method=Payment.MethodChoices.POS,
                        transaction_reference=f"POS/STANBIC/8812{idx}",
                        payment_date=date(2025, 9, 20),
                        received_by=accountant,
                        remarks='Part-payment (Tuition component paid, levies pending)'
                    )
            # idx 6, 7 remain unpaid

        AuditLog.objects.create(
            user=principal,
            action='SEED_SYSTEM',
            details='Initialized secondary school management system with comprehensive demo records'
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded secondary school management database!"))
        self.stdout.write(self.style.SUCCESS("Principal Account:  username='principal', password='password123'"))
        self.stdout.write(self.style.SUCCESS("Teacher Account:    username='teacher_math', password='password123'"))
        self.stdout.write(self.style.SUCCESS("Accountant Account: username='accountant', password='password123'"))
