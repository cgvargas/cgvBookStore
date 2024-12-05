# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Contato, CustomUser, EstanteLivro


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


class LivroManualForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título do livro'
        })
    )

    autor = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Autor do livro'
        })
    )

    capa = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL da capa (opcional)'
        })
    )

    tipo = forms.ChoiceField(
        choices=EstanteLivro.TIPO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    editora = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Editora (opcional)'
        })
    )

    data_lancamento = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Data de lançamento (opcional)'
        })
    )

    sinopse = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Sinopse do livro (opcional)',
            'rows': 4
        })
    )

    numero_paginas = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de páginas'
        })
    )

    isbn = forms.CharField(
        max_length=13,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ISBN (opcional)'
        })
    )

    idioma = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Idioma (opcional)'
        })
    )

    categoria = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Categoria/Gênero (opcional)'
        })
    )

    notas_pessoais = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Notas pessoais sobre o livro (opcional)',
            'rows': 3
        })
    )

    class Meta:
        model = EstanteLivro
        fields = [
            'titulo', 'autor', 'capa', 'tipo', 'editora',
            'data_lancamento', 'sinopse', 'numero_paginas',
            'isbn', 'idioma', 'categoria', 'notas_pessoais'
        ]

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            # Remove hífens e espaços do ISBN
            isbn = isbn.replace('-', '').replace(' ', '')
            # Verifica se o ISBN tem 10 ou 13 dígitos
            if len(isbn) not in [10, 13]:
                raise ValidationError('ISBN deve ter 10 ou 13 dígitos')
        return isbn

    def clean_numero_paginas(self):
        numero = self.cleaned_data.get('numero_paginas')
        if numero and numero < 1:
            raise ValidationError('O número de páginas deve ser maior que zero')
        return numero

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.manual = True  # Marca como livro adicionado manualmente

        if commit:
            instance.save()
        return instance