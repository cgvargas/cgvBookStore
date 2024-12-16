# core/presentation/views/recommendation_views.py
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.application.recommendations.services import RecommendationApplicationService

logger = logging.getLogger(__name__)


@login_required
def get_recommendations(request):
    """View para obter recomendações de livros"""
    try:
        service = RecommendationApplicationService()
        recommendations = service.generate_recommendations(request.user.id)

        # Formata as recomendações para JSON
        recommendations_data = [
            {
                'id': rec.livro_id,
                'titulo': rec.titulo,
                'autor': rec.autor,
                'categoria': rec.categoria,
                'score': float(rec.score),
                'imagem_url': rec.imagem_url
            }
            for rec in recommendations
        ]

        return JsonResponse({
            'status': 'success',
            'recommendations': recommendations_data
        })

    except Exception as e:
        logger.error(f"Erro ao obter recomendações: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao gerar recomendações'
        }, status=500)


@login_required
def update_preferences(request):
    """View para atualizar preferências do usuário"""
    try:
        service = RecommendationApplicationService()
        service.update_user_preferences(request.user.id)

        return JsonResponse({
            'status': 'success',
            'message': 'Preferências atualizadas com sucesso'
        })

    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao atualizar preferências'
        }, status=500)