# core/application/recommendations/services.py
import logging
from typing import List, Optional
from django.contrib.auth import get_user_model
from datetime import datetime

from core.domain.recommendations.entities import BookRecommendation, UserPreference
from core.domain.recommendations.services import RecommendationService
from core.infrastructure.persistence.django.repositories.recommendation_repository import DjangoRecommendationRepository
from core.infrastructure.persistence.django.models import LivroCache

logger = logging.getLogger(__name__)
User = get_user_model()


class RecommendationApplicationService:
    """Serviço de aplicação para recomendações"""

    def __init__(self):
        self.repository = DjangoRecommendationRepository()
        self.domain_service = RecommendationService()

    def generate_recommendations(self, user_id: int) -> List[BookRecommendation]:
        """Gera recomendações para um usuário"""
        try:
            logger.info(f"Gerando recomendações para usuário {user_id}")

            # Obtém ou cria preferências do usuário
            user_preferences = self.repository.get_user_preferences(user_id)
            if not user_preferences:
                user_preferences = UserPreference(
                    usuario_id=user_id,
                    categorias_favoritas={},
                    autores_favoritos={},
                    ultima_atualizacao=datetime.now()
                )
                self.repository.save_user_preferences(user_preferences)

            # Busca livros candidatos do cache
            cached_books = LivroCache.objects.all()[:200]  # Limitando para performance

            recommendations = []
            for book in cached_books:
                score = self.domain_service.calcular_score({
                    'categoria': book.categoria,
                    'autor': book.autor
                }, user_preferences)

                if score >= 1:
                    recommendations.append(
                        BookRecommendation(
                            livro_id=book.book_id,
                            titulo=book.titulo,
                            autor=book.autor,
                            categoria=book.categoria or '',
                            score=score,
                            imagem_url=book.imagem_url
                        )
                    )

            # Ordena e limita recomendações
            recommendations.sort(key=lambda x: x.score, reverse=True)
            top_recommendations = recommendations[:8]

            # Salva recomendações
            self.repository.save_recommendations(user_id, top_recommendations)

            logger.info(f"Geradas {len(top_recommendations)} recomendações para usuário {user_id}")
            return top_recommendations

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return []

    def update_user_preferences(self, user_id: int) -> None:
        """Atualiza as preferências do usuário baseado em seu histórico"""
        try:
            from core.infrastructure.persistence.django.models import EstanteLivro

            # Busca livros do usuário
            user_books = EstanteLivro.objects.filter(usuario_id=user_id)

            # Conta categorias e autores
            categorias = {}
            autores = {}

            for book in user_books:
                if book.categoria:
                    categorias[book.categoria] = categorias.get(book.categoria, 0) + 1
                if book.autor:
                    autores[book.autor] = autores.get(book.autor, 0) + 1

            # Atualiza preferências
            preferences = UserPreference(
                usuario_id=user_id,
                categorias_favoritas=categorias,
                autores_favoritos=autores,
                ultima_atualizacao=datetime.now()
            )

            self.repository.save_user_preferences(preferences)
            logger.info(f"Preferências atualizadas para usuário {user_id}")

        except Exception as e:
            logger.error(f"Erro ao atualizar preferências: {str(e)}")