import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import *
import os


class AuthForm(forms.Form):
    username = forms.CharField(
        label="Логин", widget=forms.TextInput(attrs={'placeholder': 'login'}))
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class SignForm(forms.Form):
    username = forms.CharField(
        label="Логин", widget=forms.TextInput(attrs={'placeholder': 'login'}))
    email = forms.EmailField(
        label="Почта", widget=forms.TextInput(attrs={'placeholder': 'email'}))
    name = forms.CharField(
        label="ФИО", widget=forms.TextInput(attrs={'placeholder': 'name'}))
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Пароль (подтверждение)")


class EventForm(forms.Form):
    name = forms.CharField(max_length=50, label="Название")
    startDate = forms.DateTimeField(initial=datetime.now, label="Дата начала")
    endDate = forms.DateTimeField(
        initial=datetime.now, label="Дата завершения")
    address = forms.CharField(max_length=50, label="Адрес")
    type = forms.ModelChoiceField(
        queryset=TypeEvent.objects.all(), to_field_name="id", label="Тип")
    description = forms.CharField(required=False, max_length=1000,
                                  label="Описание", widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))


class VisitorForm(forms.Form):
    arrivalDate = forms.DateTimeField(
        initial=datetime.now, label="Дата прибытия")
    fullName = forms.CharField(max_length=50, label="Имя")
    type = forms.ModelChoiceField(
        queryset=TypeVisitor.objects.all(), to_field_name="id", label="Тип участника")
