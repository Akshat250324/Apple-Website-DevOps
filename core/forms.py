from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from .models import CustomerDetail
from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import re

# Validator for Password Strength (Minimum length 8 characters, at least one letter and one number)
def password_strength(value):
    if not re.search(r'[A-Za-z]', value):
        raise ValidationError('Password must contain at least one letter.')
    if not re.search(r'[0-9]', value):
        raise ValidationError('Password must contain at least one number.')
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}), validators=[password_strength])
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {'email': 'Email'}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email = EmailValidator()
        validate_email(email)  # Ensure it's a valid email
        return email

class AuthenticateForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}), validators=[password_strength])
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UserProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_login': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email = EmailValidator()
        validate_email(email)  # Ensure it's a valid email
        return email

class AdminProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Custom validator for name (to ensure that name is not empty or just spaces)
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise ValidationError('Name cannot be empty or spaces only.')
        return name

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerDetail
        fields=['name','address','city','state','pincode']
        labels = {'name':'Full Name'}
        widgets = {'name':forms.TextInput(attrs={'class':'form-control'}),
                   'address':forms.TextInput(attrs={'class':'form-control'}),
                   'city':forms.TextInput(attrs={'class':'form-control'}),
                   'state':forms.Select(attrs={'class':'form-control'}),
                   'pincode':forms.NumberInput(attrs={'class':'form-control'}),
                   }
                   