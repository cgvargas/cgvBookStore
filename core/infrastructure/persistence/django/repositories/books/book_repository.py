from typing import List, Optional
from core.domain.books.entities import Book
from ..base import BaseRepository

class BookRepository(BaseRepository[Book]):
    def __init__(self):
        super().__init__(Book)

    def get_featured_books(self, order_by=None):
        """
        Retorna os livros em destaque

        Args:
            order_by: Lista de campos para ordenação

        Returns:
            QuerySet: Livros em destaque ordenados
        """
        query = self.model.objects.filter(destaque=True)
        if order_by:
            query = query.order_by(*order_by)
        return query

    def get_bestseller_books(self, order_by=None):
        """
        Retorna os livros mais vendidos

        Args:
            order_by: Lista de campos para ordenação

        Returns:
            QuerySet: Livros mais vendidos ordenados
        """
        query = self.model.objects.filter(mais_vendido=True)
        if order_by:
            query = query.order_by(*order_by)
        return query

    def get_related_books(self, book: Book, limit: int = 5) -> List[Book]:
        """Retorna livros relacionados baseado em categorias"""
        return list(self.filter(
            categorias__in=book.categorias.all()
        ).exclude(
            id=book.id
        ).distinct().order_by('?')[:limit])

    def get_book_by_id(self, book_id):
        """Retorna um livro pelo ID"""
        try:
            return self.model.objects.get(pk=book_id)
        except self.model.DoesNotExist:
            return None

    def get_featured_books(self, exclude_id=None, limit=None):
        """Retorna livros em destaque"""
        query = self.model.objects.filter(destaque=True)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        if limit:
            query = query[:limit]
        return query