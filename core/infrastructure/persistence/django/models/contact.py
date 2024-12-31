"""Models for contact persistence."""

from django.db import models


class Contact(models.Model):
    """Model representing a contact message from users."""

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        db_table = 'core_contato'
        ordering = ['-data']

    def __str__(self):
        return f'{self.nome} - {self.assunto}'