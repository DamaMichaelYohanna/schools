from django import forms
from django.utils import timezone
import uuid
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'admission_number', 'first_name', 'last_name', 'other_names',
            'gender', 'date_of_birth', 'admission_date', 'current_class',
            'passport_photo', 'blood_group', 'genotype', 'state_of_origin',
            'nationality', 'residential_address',
            'guardian_name', 'guardian_relationship', 'guardian_phone',
            'guardian_email', 'guardian_address', 'status'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. SEC/2025/001'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'other_names': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'gender': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'current_class': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'passport_photo': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'blood_group': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'genotype': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'state_of_origin': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'nationality': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'residential_address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'guardian_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'Father, Mother, Uncle, Guardian'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'guardian_address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('admission_number'):
            year = timezone.now().year
            rand_code = uuid.uuid4().hex[:4].upper()
            self.initial['admission_number'] = f"SEC/{year}/{rand_code}"
