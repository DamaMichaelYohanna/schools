from django import forms
from .models import TermReportSummary


class TermReportRemarkForm(forms.ModelForm):
    class Meta:
        model = TermReportSummary
        fields = [
            'days_present', 'total_school_days',
            'teacher_remark', 'principal_remark', 'next_term_resumption'
        ]
        widgets = {
            'days_present': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'total_school_days': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'teacher_remark': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'principal_remark': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'next_term_resumption': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }
