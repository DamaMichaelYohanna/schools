from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition text-slate-800 placeholder-slate-400',
            'placeholder': 'Enter your username or Staff ID',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition text-slate-800 placeholder-slate-400',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )


class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none',
            'placeholder': 'Temporary access password'
        }),
        help_text='Staff member will use this to sign in.'
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'role',
            'staff_id', 'phone_number', 'gender', 'qualification',
            'date_employed', 'avatar', 'address', 'password'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'staff_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. STF-2025-001'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'gender': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'qualification': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none', 'placeholder': 'e.g. B.Sc Mathematics, PGDE'}),
            'date_employed': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'avatar': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class StaffEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role',
            'staff_id', 'phone_number', 'gender', 'qualification',
            'date_employed', 'avatar', 'address', 'is_active_staff'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'staff_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'gender': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'qualification': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'date_employed': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'avatar': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-400 outline-none'}),
            'is_active_staff': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500'}),
        }
