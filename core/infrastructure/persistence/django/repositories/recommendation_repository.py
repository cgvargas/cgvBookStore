# core/infrastructure/persistence/django/repositories/recommendation_repository.py
from typing import List, Optional
from django.db import transaction
from core.domain.recommendations.entities import BookRecommendation, UserPreference
from ..models.recommendations import NewUserPreferences, NewLivroRecomendado


class DjangoRecommendationRepository:
    def get_user_recommendations(self, user_id: int) -> List[NewLivroRecomendado]:
        """Retorna as recomendações de livros para um usuário"""
        return NewLivroRecomendado.objects.filter(
            usuario_id=user_id
        ).order_by('-score')

    def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        try:
            prefs = NewUserPreferences.objects.get(usuario_id=user_id)
            return prefs.to_domain()
        except NewUserPreferences.DoesNotExist:
            return None

    def save_user_preferences(self, preferences: UserPreference) -> None:
        NewUserPreferences.objects.update_or_create(
            usuario_id=preferences.usuario_id,
            defaults={
                'categorias_favoritas': preferences.categorias_favoritas,
                'autores_favoritos': preferences.autores_favoritos,
                'ultima_atualizacao': preferences.ultima_atualizacao
            }
        )

    @transaction.atomic
    def save_recommendations(self, user_id: int, recommendations: List[BookRecommendation]) -> None:
        # Remove recomendações antigas
        NewLivroRecomendado.objects.filter(usuario_id=user_id).delete()

        # Salva novas recomendações
        NewLivroRecomendado.objects.bulk_create([
            NewLivroRecomendado(
                usuario_id=user_id,
                livro_id=rec.livro_id,
                titulo=rec.titulo,
                autor=rec.autor,
                categoria=rec.categoria,
                score=rec.score
            ) for rec in recommendations
        ])