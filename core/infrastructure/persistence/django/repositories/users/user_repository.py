from core.models import CustomUser
from ..base import BaseRepository

class UserRepository(BaseRepository[CustomUser]):
    def __init__(self):
        super().__init__(CustomUser)

    def get_by_username(self, username: str):
        """Retorna usuário pelo username"""
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None

    def get_by_email(self, email: str):
        """Retorna usuário pelo email"""
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None

    def update_user_profile_photo(self, user: CustomUser, photo_path) -> CustomUser:
        """Atualiza a foto de perfil do usuário"""
        try:
            user.profile_image = photo_path
            user.save()
            return user
        except Exception as e:
            raise Exception(f"Erro ao atualizar a foto de perfil: {e}")
