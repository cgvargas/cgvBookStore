"""
Domain entities for the contact module.
This module contains entities related to user contact and messaging.
"""

from django.db import models


class Contact(models.Model):
    """Entity representing a contact message from users."""

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        db_table = 'core_contato'  # Mantém compatibilidade com banco existente
        ordering = ['-data']

    def __str__(self):
        return f'{self.nome} - {self.assunto}'

    def get_summary(self):
        """Returns a summary of the contact message"""
        return {
            'nome': self.nome,
            'email': self.email,
            'assunto': self.assunto,
            'data': self.data.strftime('%d/%m/%Y %H:%M'),
            'mensagem_preview': self.mensagem[:100] + '...' if len(self.mensagem) > 100 else self.mensagem
        }