# 🎓 Secondary School Management System

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A modern, robust, and full-featured Secondary School Management Platform built with **Django**, **HTML5**, **CSS3**, and **Tailwind CSS**. Designed for secondary schools following standard academic calendar systems (3-Term calendar, Continuous Assessment & Examinations, Class Arms, Student Records, Bursary/Finance, and Staff Roles).

---

## 🏛️ System Features & Capabilities

### 1. 🎨 Database-Controlled School Branding
- **Dynamic Identity**: School name, motto, email, phone, physical address, and official crest/logo are stored in the database.
- **Admin & Web UI Management**: Changeable via both the frontend dashboard ([`/settings/`](http://127.0.0.1:8000/settings/)) and standard Django Admin ([`/admin/`](http://127.0.0.1:8000/admin/)).
- **Universal Template Injection**: A custom context processor automatically applies branding across navigation headers, terminal report cards, and fee receipts.

### 2. 🔐 Role-Based Access Control (RBAC) & Staff Portal
- **Custom User Model**: Built-in support for distinct roles:
  - **Principal / Administrator**: Full school management, staff creation, role assignment, school identity, and financial oversight.
  - **Subject Teacher**: View assigned classes, batch upload Continuous Assessment and Examination marks, enter class remarks.
  - **Accountant / Bursar**: Manage fee structures, issue invoices, record tuition payments, and generate official receipts.
- **Role Decorators & Permissions**: `@principal_required`, `@teacher_required`, and `@accountant_required` protect critical routes.

### 3. 📅 Academic Structure & Dynamic Calendar
- **Academic Sessions & 3-Term Calendar**: Supports 1st, 2nd, and 3rd Term tracking with automated system-wide term switching.
- **Secondary School Levels & Arms**: JSS 1 to SSS 3 with sections (e.g. *JSS 1A*, *SSS 2 Science*).
- **Curriculum & Teacher Allocation**: Principal assigns subjects to teachers for specific class arms (e.g., *Mr. Adeyemi &rarr; Mathematics &rarr; JSS 1A*).

### 4. 👨‍🎓 Student Records (360° Profile)
- Comprehensive bio-data, unique admission numbers, passport photos, medical records (blood group, genotype), and emergency parent/guardian contacts.
- Quick search and filtering by class arm and status (Active, Graduated, Suspended).
- Student detail view with historical academic report cards and invoice payment ledgers.

### 5. 📊 Continuous Assessment & Examination System
- **Assessment Weighting**: CA 1 (15) + CA 2 (15) + CA 3 (10) + Exam (60) = Total (100).
- **Interactive Batch Score Entry**: Live client-side auto-computation of totals, letter grades (`A1`, `B2`, `B3`, `C4`, `C5`, `C6`, `D7`, `E8`, `F9`), and qualitative remarks.
- **Automated Class Rankings**: Real-time position calculation for all students in each class.
- **Master Broadsheet**: Composite score sheet matrix of all students across all subjects.
- **Print-Ready Terminal Report Cards**: Single-page A4 print layout (`@media print`) featuring school crest, student photo, attendance, subject marks, class position, teacher remarks, and digital principal signature.

### 6. 💰 Bursary & Financial Accounting
- **Fee Structures**: Configurable fee schedules per class level and term (Tuition, Development levy, ICT lab, PTA levy).
- **Invoice Engine**: Batch invoice generation for an entire class or the whole school.
- **Payment Collection**: Records Cash, Bank Transfer, POS, or Cheque payments, automatically updating student balances and status (`UNPAID` &rarr; `PARTIAL` &rarr; `PAID`).
- **Official Fee Receipts**: Auto-generated sequential receipts with printable styling for accounting records.

---

## 📂 Project Structure

```
schools/
├── manage.py
├── requirements.txt
├── LICENSE
├── README.md
├── school_system/             # Core Project Configuration
│   ├── settings.py            # Custom User, Apps, Context Processors, Media
│   ├── urls.py                # Main URL routing & static/media serving
│   └── wsgi.py
├── apps/
│   ├── core/                  # Branding Singleton, Dashboard & Audit Logs
│   ├── accounts/              # Staff Authentication & Role Management
│   ├── academics/             # Sessions, Terms, Classes, Subjects & Allocations
│   ├── students/              # Learner Records & Profiles
│   ├── results/               # Scores, Broadsheet & Report Cards
│   └── finance/               # Bursary, Invoices, Payments & Receipts
├── templates/                 # Tailwind CSS Responsive UI & Print Templates
│   ├── base.html
│   ├── accounts/
│   ├── academics/
│   ├── core/
│   ├── finance/
│   ├── results/
│   └── students/
└── static/                    # CSS, JavaScript & Static Assets
```

---

## ⚡ Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/DamaMichaelYohanna/schools.git
cd schools
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Seed Realistic Demo Data
Populate the database with demo staff accounts, classes, subjects, student records, assessment scores, fee invoices, and receipts:
```bash
python manage.py seed_school_data
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 🔑 Pre-Seeded Demo Credentials

| Role | Username | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Principal / Admin** | `principal` | `password123` | Full administrative control, staff creation, branding settings, calendar, and analytics. |
| **Mathematics Teacher** | `teacher_math` | `password123` | Score entry for assigned classes (JSS 1A, JSS 2A, SSS 1 Science), broadsheets. |
| **English Teacher** | `teacher_eng` | `password123` | Score entry for English Language, class teacher remarks. |
| **Accountant / Bursar** | `accountant` | `password123` | Invoicing, payment recording, fee collection ledger, and official receipts. |

---

## 🧪 Running Automated Tests

To run the complete unit and integration test suite:

```bash
python manage.py test apps.core
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
