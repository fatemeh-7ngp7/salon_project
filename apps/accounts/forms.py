from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re


class LoginForm(forms.Form):
    phone = forms.CharField(
        max_length=11,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '09123456789',
            'dir': 'ltr'
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^09[0-9]{9}$', phone):
            raise forms.ValidationError('شماره موبایل معتبر نیست.')
        return phone


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        label='نام',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=50,
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=11,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '09123456789',
            'dir': 'ltr'
        })
    )
    email = forms.EmailField(
        required=False,
        label='ایمیل (اختیاری)',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^09[0-9]{9}$', phone):
            raise forms.ValidationError('شماره موبایل معتبر نیست.')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('این شماره موبایل قبلاً ثبت شده است.')
        return phone