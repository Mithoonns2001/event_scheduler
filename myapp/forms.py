from django import forms
from django.contrib.auth.models import User
from .models import Employee

class EmployeeRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    employee_id = forms.CharField(max_length=20)

class EmployeeLoginForm(forms.Form):
    employee_id = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class HeadLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
