# core/infrastructure/persistence/django/models/__init__.py
from .recommendations import NewLivroRecomendado, NewUserPreferences
from .cache import NewLivroCache

__all__ = ['NewLivroRecomendado', 'NewUserPreferences', 'NewLivroCache']