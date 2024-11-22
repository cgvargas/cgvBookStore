# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contato
from django.utils import timezone


class ContatoForm(forms.ModelForm):

    class Meta:
        model = Contato
        fields = ['nome', 'email', 'assunto', 'mensagem']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.data:
            instance.data = timezone.now().date()  # Define a data atual
        if commit:
            instance.save()
        return instance


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
