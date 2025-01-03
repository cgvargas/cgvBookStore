from typing import List
from datetime import datetime
from core.domain.users.entities import ActivityHistory, CustomUser
from ..base import BaseRepository

class ActivityHistoryRepository(BaseRepository[ActivityHistory]):
    def __init__(self):
        super().__init__(ActivityHistory)

    def log_activity(self, user: CustomUser, action: str, details: str = None) -> ActivityHistory:
        """Registra uma nova atividade"""
        return self.create(
            usuario=user,
            acao=action,
            detalhes=details,
            data=datetime.now()
        )

    def get_user_activities(self, user: CustomUser, limit: int = None) -> List[ActivityHistory]:
        """Retorna histórico de atividades do usuário"""
        activities = self.filter(usuario=user).order_by('-data')
        if limit:
            activities = activities[:limit]
        return list(activities)

    def register_book_transfer(self, user, book_id, book_title, old_type, new_type):
        """Registra a transferência de um livro entre prateleiras"""
        try:
            return self.model_class.objects.create(
                usuario=user,
                acao='transferencia',
                livro_id=book_id,
                titulo_livro=book_title,
                detalhes=f"Livro transferido de {old_type} para {new_type}",
                data=datetime.now()
            )
        except Exception as e:
            print(f"Erro ao registrar transferência: {str(e)}")
            # Retorna None mas não impede a transferência
            return None