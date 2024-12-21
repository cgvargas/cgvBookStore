from typing import List
from django.contrib.auth import get_user_model
from core.domain.books.entities import BookShelf, Book
from ..base import BaseRepository

User = get_user_model()

class BookShelfRepository(BaseRepository[BookShelf]):
    def __init__(self):
        super().__init__(BookShelf)

    def get_user_books_by_type(self, user, tipo, include_book_data=True):
        """Retorna livros do usuário por tipo, otimizados com select_related"""
        query = self.filter(usuario=user, tipo=tipo)
        if include_book_data:
            query = query.select_related('livro')
        return query.order_by('-data_adicao')

    def count_valid_user_books(self, user):
        """Conta total de livros válidos do usuário"""
        return self.filter(
            usuario=user,
            titulo__isnull=False
        ).distinct().count()

    def book_exists_in_shelf(self, user, book_id):
        """Verifica se um livro já existe na estante do usuário"""
        return self.model.objects.filter(usuario=user, livro_id=book_id).exists()

    def add_google_book_to_shelf(self, user, google_book_id, book_type, book_data):
        """Adiciona um livro do Google Books à estante"""
        return self.model.objects.create(
            usuario=user,
            livro_id=google_book_id,
            tipo=book_type,
            titulo=book_data.get('titulo', ''),
            autor=book_data.get('autor', ''),
            capa=book_data.get('imagem', ''),
            data_lancamento=book_data.get('data_publicacao', ''),
            sinopse=book_data.get('descricao', ''),
            editora=book_data.get('editora', ''),
            numero_paginas=book_data.get('numero_paginas'),
            isbn=book_data.get('isbn', ''),
            idioma=book_data.get('idioma', ''),
            categoria=book_data.get('categoria', ''),
            manual=False
        )

    def transfer_book(self, user, book_id, new_type):
        """Transfere um livro para outra prateleira"""
        try:
            livro = self.model.objects.get(id=book_id, usuario=user)
            if new_type in dict(self.model.TIPO_CHOICES):
                livro.tipo = new_type
                livro.save()
                return livro
            return None
        except self.model.DoesNotExist:
            return None

    def add_book_to_shelf(self, user, book_data):
        """
        Adiciona um livro à estante do usuário

        Args:
            user: Usuário que está adicionando o livro
            book_data: Dicionário com os dados do livro

        Returns:
            EstanteLivro: O livro adicionado
        """
        return self.model.objects.create(
            usuario=user,
            **book_data
        )
