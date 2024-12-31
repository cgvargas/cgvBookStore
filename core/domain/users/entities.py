from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Entidade principal que representa um usuário no sistema."""

    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_registro = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )

    # Atualizando related_names para evitar conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_users',  # Alterado aqui
        related_query_name='core_user'  # Alterado aqui
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_users',  # Alterado aqui
        related_query_name='core_user'  # Alterado aqui
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'core_customuser'  # Mantém compatibilidade com banco existente

    def __str__(self):
        return self.username

    def get_profile_image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return None


class ActivityHistory(models.Model):
    """Entidade para rastrear atividades do usuário no sistema."""

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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