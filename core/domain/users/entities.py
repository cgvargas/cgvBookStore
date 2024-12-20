"""
Domain entities for the users module.
This module contains the core business entities related to users and their activities.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Core entity representing a user in the system."""

    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_registro = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )

    # Resolvendo os conflitos de relacionamento
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser'
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'core_customuser'  # Mantém compatibilidade com banco existente

    def __str__(self):
        return self.username

    def get_profile_image_url(self):
        """Returns the URL of the profile image or None if there isn't one"""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return None


class ActivityHistory(models.Model):
    """Entity for tracking user activities in the system."""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=50)
    livro_id = models.CharField(max_length=100)
    titulo_livro = models.CharField(max_length=255)
    detalhes = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Histórico de Atividade'
        verbose_name_plural = 'Histórico de Atividades'
        db_table = 'core_historicoatividade'  # Mantém compatibilidade com banco existente

    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.titulo_livro}"

    @classmethod
    def register_activity(cls, user, action, book_id, book_title, details=""):
        """
        Utility method to register a new activity.

        Args:
            user: The user performing the action
            action: The action being performed
            book_id: ID of the book involved
            book_title: Title of the book
            details: Additional details about the activity
        """
        return cls.objects.create(
            usuario=user,
            acao=action,
            livro_id=book_id,
            titulo_livro=book_title,
            detalhes=details
        )

    def get_activity_summary(self):
        """Returns a human-readable summary of the activity"""
        return f"{self.get_acao_display()} - {self.titulo_livro} em {self.data.strftime('%d/%m/%Y %H:%M')}"