# core/presentation/forms/contact/contact_form.py
from django import forms
from django.utils import timezone
from core.infrastructure.persistence.django.models.contact import Contact


class ContatoForm(forms.ModelForm):
    """
    Formulário para contato integrado com a entidade Contact do domínio.
    """
    class Meta:
        model = Contact
        fields = ['nome', 'email', 'assunto', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Seu nome',
                'id': 'id_nome',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Seu email',
                'id': 'id_email',
                'required': True
            }),
            'assunto': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Assunto da mensagem',
                'id': 'id_assunto',
                'required': True
            }),
            'mensagem': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Sua mensagem',
                'rows': 4,
                'id': 'id_mensagem',
                'required': True
            })
        }

    def save(self, commit=True):
        """
        Salva o formulário garantindo que a data seja definida.
        """
        instance = super().save(commit=False)
        if not instance.data:
            instance.data = timezone.now().date()
        if commit:
            instance.save()
        return instance