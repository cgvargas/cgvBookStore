# core/infrastructure/persistence/django/models/recommendations.py
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class LivroRecomendado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    livro_id = models.CharField(max_length=100)
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    data_recomendacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', 'titulo']
        unique_together = ['usuario', 'livro_id']

    def __str__(self):
        return f"{self.titulo} ({self.score})"


class UserPreferences(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    categorias_favoritas = models.JSONField(default=dict)
    autores_favoritos = models.JSONField(default=dict)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferências de {self.usuario.username}"