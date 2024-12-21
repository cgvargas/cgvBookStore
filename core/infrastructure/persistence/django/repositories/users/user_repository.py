from typing import Optional
from core.domain.users.entities import User
from ..base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Retorna usuário pelo username"""
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Retorna usuário pelo email"""
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None