# core/infrastructure/persistence/django/repositories/books/book_repository.py
from core.domain.books.entities import Book
from ..base import BaseRepository


class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__(model_class=Book)

    def get_book_by_id(self, book_id):
        """
        Retorna um livro específico pelo ID.
        """
        try:
            return self.model_class.objects.select_related().get(id=book_id)
        except self.model_class.DoesNotExist:
            return None

    def get_featured_books(self, order_by=None, exclude_id=None, limit=None):
        query = self.model_class.objects.filter(destaque=True)

        if exclude_id:
            query = query.exclude(id=exclude_id)

        if order_by:
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)

        if limit:
            query = query[:limit]

        return query.only(
            'id', 'titulo', 'autor', 'imagem',
            'data_publicacao', 'categoria', 'destaque'
        )

    def get_bestseller_books(self, order_by=None, limit=None):
        query = self.model_class.objects.filter(mais_vendido=True)

        if order_by:
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)

        if limit:
            query = query[:limit]

        return query.only(
            'id', 'titulo', 'autor', 'imagem',
            'data_publicacao', 'categoria', 'mais_vendido'
        )

    def get_featured_books_with_details(self, exclude_id=None, limit=None):
        """
        Retorna livros em destaque com todos os detalhes.
        """
        query = self.model_class.objects.filter(destaque=True)

        if exclude_id:
            query = query.exclude(id=exclude_id)

        if limit:
            query = query[:limit]

        return query

    def get_related_books(self, book_id, categoria=None, limit=3):
        """
        Retorna livros relacionados baseados na categoria ou outros critérios.
        """
        query = self.model_class.objects.exclude(id=book_id)

        if categoria:
            query = query.filter(categoria=categoria)

        return query[:limit]

    def update_user_profile_photo(self, user, photo_path):
        """
        Atualiza a foto de perfil do usuário.
        """
        try:
            user.profile_image = photo_path
            user.save()
            return user
        except Exception as e:
            raise Exception(f"Erro ao atualizar a foto de perfil: {e}")
