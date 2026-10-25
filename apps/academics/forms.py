from django import forms
from .models import AcademicSession, AcademicTerm, ClassLevel, ClassSection, Subject, SubjectAllocation
from django.contrib.auth import get_user_model

User = get_user_model()


class SubjectAllocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role=User.Role.TEACHER, is_active_staff=True)

    class Meta:
        model = SubjectAllocation
        fields = ['teacher', 'subject', 'class_section', 'academic_session']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'subject': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'class_section': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'academic_session': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'is_elective', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. Further Mathematics'}),
            'code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. FMTH'}),
            'is_elective': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }


class ClassSectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_teacher'].queryset = User.objects.filter(role=User.Role.TEACHER, is_active_staff=True)
        self.fields['class_teacher'].required = False
        self.fields['class_teacher'].empty_label = "--- Select Class Teacher / Staff (Optional) ---"
        self.fields['class_teacher'].help_text = "Select the designated class teacher/form master. You can also assign or change this anytime later."

    class Meta:
        model = ClassSection
        fields = ['class_level', 'name', 'class_teacher']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. A, B, Gold, Science'}),
            'class_teacher': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. 2025/2026'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500'}),
        }


class AcademicTermForm(forms.ModelForm):
    class Meta:
        model = AcademicTerm
        fields = ['session', 'term_type', 'start_date', 'end_date', 'is_current']
        widgets = {
            'session': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'term_type': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500'}),
        }
