# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Contato
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import CustomUser


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
    nome_completo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu e-mail'
        })
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escolha um nome de usuário'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('nome_completo', 'username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        return email


# Adicione um formulário de autenticação customizado
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nome de usuário'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Senha'
    }))