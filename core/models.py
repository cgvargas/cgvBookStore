# core/models.py
"""
Este arquivo agora serve apenas como ponto de importação central dos modelos.
Os modelos reais estão em seus respectivos módulos de domínio.
"""

from core.domain.books.entities import Book as Livro
from core.domain.books.entities import BookCache as LivroCache
from core.domain.books.entities import BookShelf as EstanteLivro
from core.domain.users.entities import CustomUser
from core.domain.users.entities import ActivityHistory as HistoricoAtividade
from core.domain.media.entities import ExternalURL as URLExterna
from core.domain.media.entities import YouTubeVideo as VideoYouTube
from core.infrastructure.persistence.django.models.contact import Contact as Contato

# Exporta os modelos com seus nomes originais para manter compatibilidade
__all__ = [
    'Livro',
    'LivroCache',
    'EstanteLivro',
    'CustomUser',
    'HistoricoAtividade',
    'URLExterna',
    'VideoYouTube',
    'Contato'
]