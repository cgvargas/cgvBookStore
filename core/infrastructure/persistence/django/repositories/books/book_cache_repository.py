from datetime import datetime, timedelta
from typing import Optional
from core.domain.books.entities import BookCache, Book
from ..base import BaseRepository

class BookCacheRepository(BaseRepository[BookCache]):
    def __init__(self):
        super().__init__(BookCache)

    def get_or_create_cache(self, book: Book) -> BookCache:
        """Obtém ou cria cache para um livro"""
        cache, created = self.model.objects.get_or_create(
            book=book,
            defaults={'last_updated': datetime.now()}
        )
        return cache

    def clean_old_caches(self, days: int = 30) -> int:
        """Limpa caches antigos"""
        threshold = datetime.now() - timedelta(days=days)
        old_caches = self.filter(data_cache__lt=threshold)
        count = old_caches.count()
        old_caches.delete()
        return count