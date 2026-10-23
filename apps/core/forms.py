from django import forms
from .models import SchoolSetting


class SchoolSettingForm(forms.ModelForm):
    class Meta:
        model = SchoolSetting
        fields = [
            'school_name', 'school_motto', 'school_logo', 'email', 'phone',
            'address', 'website', 'current_session', 'current_term',
            'principal_signature', 'currency_symbol',
            'ca1_max', 'ca2_max', 'ca3_max', 'exam_max'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'school_motto': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'school_logo': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'current_session': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'current_term': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'principal_signature': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'ca1_max': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'ca2_max': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'ca3_max': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'exam_max': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }
