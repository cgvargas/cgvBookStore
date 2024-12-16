# core/infrastructure/persistence/django/repositories/recommendation_repository.py
from typing import List, Optional
from django.db import transaction

from core.domain.recommendations.entities import BookRecommendation, UserPreference
from ..models.recommendations import LivroRecomendado, UserPreferences
from django.contrib.auth import get_user_model

User = get_user_model()


class DjangoRecommendationRepository:
    """Implementação do repositório de recomendações usando Django"""

    @staticmethod
    def get_user_preferences(user_id: int) -> Optional[UserPreference]:
        """Obtém as preferências do usuário"""
        try:
            prefs = UserPreferences.objects.get(usuario_id=user_id)
            return UserPreference(
                usuario_id=user_id,
                categorias_favoritas=prefs.categorias_favoritas,
                autores_favoritos=prefs.autores_favoritos,
                ultima_atualizacao=prefs.ultima_atualizacao
            )
        except UserPreferences.DoesNotExist:
            return None

    @staticmethod
    def save_user_preferences(preferences: UserPreference) -> None:
        """Salva as preferências do usuário"""
        UserPreferences.objects.update_or_create(
            usuario_id=preferences.usuario_id,
            defaults={
                'categorias_favoritas': preferences.categorias_favoritas,
                'autores_favoritos': preferences.autores_favoritos,
                'ultima_atualizacao': preferences.ultima_atualizacao
            }
        )

    @staticmethod
    @transaction.atomic
    def save_recommendations(user_id: int, recommendations: List[BookRecommendation]) -> None:
        """Salva uma lista de recomendações para um usuário"""
        # Remove recomendações anteriores
        LivroRecomendado.objects.filter(usuario_id=user_id).delete()

        # Cria as novas recomendações
        bulk_recommendations = [
            LivroRecomendado(
                usuario_id=user_id,
                livro_id=rec.livro_id,
                titulo=rec.titulo,
                autor=rec.autor,
                categoria=rec.categoria,
                score=rec.score
            )
            for rec in recommendations
        ]

        if bulk_recommendations:
            LivroRecomendado.objects.bulk_create(bulk_recommendations)

    @staticmethod
    def get_recommendations(user_id: int) -> List[BookRecommendation]:
        """Obtém as recomendações de um usuário"""
        recommendations = LivroRecomendado.objects.filter(usuario_id=user_id)
        return [
            BookRecommendation(
                livro_id=rec.livro_id,
                titulo=rec.titulo,
                autor=rec.autor,
                categoria=rec.categoria,
                score=rec.score
            )
            for rec in recommendations
        ]