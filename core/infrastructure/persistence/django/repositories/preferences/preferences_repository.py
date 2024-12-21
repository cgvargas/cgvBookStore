from core.infrastructure.persistence.django.repositories.base import BaseRepository
from core.infrastructure.persistence.django.models import NewUserPreferences


class UserPreferencesRepository(BaseRepository):
    model = NewUserPreferences

    def get_or_create_preferences(self, user):
        """
        Get or create user preferences.

        Args:
            user: User instance

        Returns:
            Tuple[NewUserPreferences, bool]: Tuple containing the preferences and
            a boolean indicating if it was created
        """
        return self.model.objects.get_or_create(usuario=user)