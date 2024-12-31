from datetime import datetime, timedelta
from typing import Optional
from core.domain.books.entities import BookCache, Book
from ..base import BaseRepository

class BookCacheRepository(BaseRepository[BookCache]):
    def __init__(self):
        super().__init__(BookCache)

    def get_book_by_id(self, book_id: str) -> Optional[BookCache]:
        """Retorna um livro do cache pelo ID"""
        try:
            return self.model_class.objects.get(book_id=book_id)
        except self.model_class.DoesNotExist:
            return None

    def get_or_create_cache(self, book: Book) -> BookCache:
        """Obtém ou cria cache para um livro"""
        cache, created = self.model_class.objects.get_or_create(
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

    def save_book(self, book_id: str, book_data: dict) -> BookCache:
        """Salva ou atualiza um livro no cache"""
        return self.model_class.objects.salvar_book(book_id, book_data)