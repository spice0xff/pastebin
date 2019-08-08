from django import forms
from django.forms import ModelForm

from core_app.models import Paste


# Форма добавлния пасты.
class PasteForm(ModelForm):
    class Meta:
        model = Paste
        fields = ['code_language', 'text', 'access_period', 'access_only_from_link', 'private']


# Форма регистраци.
class RegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )


# Форма авторизации.
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )


# Форма поиска.
class FindForm(forms.Form):
    text = forms.CharField(
        widget=forms.TextInput()
    )
