from django import forms
from django.core.exceptions import ValidationError
from core.domain.books.entities import BookShelf as EstanteLivro


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

    classificacao = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Classificação (1-5)',
        })
    )

    class Meta:
        model = EstanteLivro
        fields = [
            'titulo', 'autor', 'capa', 'tipo', 'editora',
            'data_lancamento', 'sinopse', 'numero_paginas',
            'isbn', 'idioma', 'categoria', 'notas_pessoais',
            'classificacao'
        ]

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            isbn = isbn.replace('-', '').replace(' ', '')
            if len(isbn) not in [10, 13]:
                raise ValidationError('ISBN deve ter 10 ou 13 dígitos')
            return isbn
        return ''

    def clean_numero_paginas(self):
        numero = self.cleaned_data.get('numero_paginas')
        if numero and numero < 1:
            raise ValidationError('O número de páginas deve ser maior que zero')
        return numero

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.manual = True
        if commit:
            instance.save()
        return instance