from django import forms
from .models import Payment, Invoice, FeeCategory, FeeStructure
from apps.academics.models import ClassLevel, AcademicSession, AcademicTerm, ClassSection


class PaymentRecordForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'payment_method', 'transaction_reference', 'payment_date', 'remarks']
        widgets = {
            'invoice': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': '0.00', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'Bank Ref / Teller No / Slip ID'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'Optional payment description or note'}),
        }


class InvoiceGenerateForm(forms.Form):
    academic_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'})
    )
    academic_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'})
    )
    class_section = forms.ModelChoiceField(
        queryset=ClassSection.objects.all(),
        required=False,
        empty_label="All Classes (Entire School)",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'})
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'})
    )


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. Tuition Fee'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['fee_category', 'class_level', 'academic_session', 'academic_term', 'amount']
        widgets = {
            'fee_category': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'class_level': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'academic_session': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'academic_term': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': '0.00'}),
        }
