# core/infrastructure/persistence/django/models/recommendations.py
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from collections import Counter
from datetime import datetime

User = get_user_model()

class NewUserPreferences(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    categorias_favoritas = models.JSONField(default=dict)
    autores_favoritos = models.JSONField(default=dict)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Preferência do Usuário'
        verbose_name_plural = 'Preferências dos Usuários'

    def atualizar_preferencias(self):
        """Atualiza as preferências baseado no histórico de leitura"""
        from core.models import EstanteLivro  # Import local para evitar circular import

        # Busca todos os livros do usuário
        livros = EstanteLivro.objects.filter(usuario=self.usuario)

        # Inicializa contadores
        categorias = Counter()
        autores = Counter()

        # Pesos para diferentes tipos de estante
        pesos = {
            'favorito': 2.0,
            'lido': 1.5,
            'lendo': 1.2,
            'vou_ler': 1.0
        }

        # Analisa cada livro
        for livro in livros:
            peso = pesos.get(livro.tipo, 1.0)

            # Adiciona peso extra para livros com boa classificação
            if livro.classificacao:
                peso *= (1 + (livro.classificacao - 3) * 0.1)

            if livro.categoria:
                categorias[livro.categoria] += peso
            if livro.autor:
                autores[livro.autor] += peso

        # Atualiza as preferências
        self.categorias_favoritas = dict(categorias.most_common(10))
        self.autores_favoritos = dict(autores.most_common(10))
        self.save()

    def calcular_score_livro(self, livro):
        """Calcula o score de compatibilidade de um livro com as preferências"""
        base_score = 1.0

        try:
            # Pontuação por categoria
            if livro.categoria and self.categorias_favoritas:
                categoria_livro = livro.categoria.lower().strip()
                for cat_pref, peso in self.categorias_favoritas.items():
                    if cat_pref.lower() in categoria_livro or categoria_livro in cat_pref.lower():
                        base_score += float(peso)

            # Pontuação por autor
            if livro.autor and self.autores_favoritos:
                autor_livro = livro.autor.lower().strip()
                for autor_pref, peso in self.autores_favoritos.items():
                    if autor_pref.lower() in autor_livro or autor_livro in autor_pref.lower():
                        base_score += float(peso)

            # Normaliza o score para um intervalo de 1 a 5
            normalized_score = min(5.0, max(1.0, base_score))
            return normalized_score

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao calcular score para '{livro.titulo}': {str(e)}")
            return 1  # Score mínimo em caso de erro

class NewLivroRecomendado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    livro_id = models.CharField(max_length=100)
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    data_recomendacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Livro Recomendado'
        verbose_name_plural = 'Livros Recomendados'
        ordering = ['-score', 'titulo']

    def __str__(self):
        return f"{self.titulo} ({self.score})"