# core/infrastructure/persistence/django/books/bookshelf_repository.py
from django.contrib.auth import get_user_model
from core.domain.books.entities import BookShelf, Book
from ..base import BaseRepository
import logging
from core.domain.books.entities import BookShelf as EstanteLivro

logger = logging.getLogger(__name__)

User = get_user_model()

class BookShelfRepository(BaseRepository[BookShelf]):
    def __init__(self):
        super().__init__(BookShelf)

    def get_user_books_by_type(self, user, book_type):
        """Retorna os livros de um tipo específico para um usuário"""
        return self.model_class.objects.filter(
            usuario=user,
            tipo=book_type
        ).order_by('titulo')

    def count_valid_user_books(self, user):
        """Conta total de livros válidos do usuário"""
        return self.filter(
            usuario=user,
            titulo__isnull=False
        ).distinct().count()

    def book_exists_in_shelf(self, user, book_id):
        """Verifica se um livro já existe na estante do usuário"""
        return self.model_class.objects.filter(usuario=user, livro_id=book_id).exists()

    def add_google_book_to_shelf(self, user, google_book_id, book_type, book_data):
        """Adiciona um livro do Google Books à estante"""
        # Trata o número de páginas
        numero_paginas = book_data.get('numero_paginas')
        if not isinstance(numero_paginas, int) or numero_paginas == "Não disponível":
            numero_paginas = 0  # Valor padrão quando não disponível

        return self.model_class.objects.create(
            usuario=user,
            livro_id=google_book_id,
            tipo=book_type,
            titulo=book_data.get('titulo', ''),
            autor=book_data.get('autor', ''),
            capa=book_data.get('imagem', ''),
            data_lancamento=book_data.get('data_publicacao', ''),
            sinopse=book_data.get('descricao', ''),
            editora=book_data.get('editora', ''),
            numero_paginas=numero_paginas,
            isbn=book_data.get('isbn', ''),
            idioma=book_data.get('idioma', ''),
            categoria=book_data.get('categoria', ''),
            manual=False
        )

    def transfer_book(self, user, book_id, new_type):
        """Transfere um livro para outra prateleira"""
        try:
            livro = self.model_class.objects.get(id=book_id, usuario=user)
            if new_type in dict(self.model_class.TIPO_CHOICES):
                livro.tipo = new_type
                livro.save()
                return livro
            return None
        except self.model_class.DoesNotExist:
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
        return self.model_class.objects.create(
            usuario=user,
            **book_data
        )

    def get_user_book_by_google_id(self, user, google_book_id):
        """
        Busca um livro na estante do usuário pelo ID do Google Books

        Args:
            user: Usuário dono da estante
            google_book_id: ID do livro no Google Books

        Returns:
            EstanteLivro: Livro encontrado ou None
        """
        try:
            return EstanteLivro.objects.get(
                usuario=user,
                livro_id=google_book_id
            )
        except EstanteLivro.MultipleObjectsReturned:
            # Se existirem múltiplos, retorna o primeiro
            return EstanteLivro.objects.filter(
                usuario=user,
                livro_id=google_book_id
            ).first()
        except EstanteLivro.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar livro por Google ID: {str(e)}")
            return None

    def get_user_books_by_id(self, user, book_id):
        """
        Busca um livro na estante do usuário por ID

        Args:
            user: Usuário dono da estante
            book_id: ID do livro (pode ser numérico ou Google Books ID)

        Returns:
            EstanteLivro: Livro encontrado ou None
        """
        try:
            # Primeiro tenta buscar por ID numérico
            try:
                return self.model_class.objects.get(
                    usuario=user,
                    id=int(book_id)
                )
            except ValueError:
                # Se não for um ID numérico, tenta buscar como Google Books ID
                return self.model_class.objects.get(
                    usuario=user,
                    livro_id=book_id
                )
        except self.model_class.DoesNotExist:
            logger.warning(f"Livro {book_id} não encontrado para o usuário {user}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar livro {book_id}: {str(e)}")
            return None

    def update_manual_book(self, user, book_id, book_data):
        """Atualiza um livro na estante"""
        try:
            # Primeiro tenta buscar por ID numérico
            try:
                book = self.model_class.objects.get(
                    usuario=user,
                    id=int(book_id)
                )
            except ValueError:
                # Se não for um ID numérico, tenta buscar como Google Books ID
                book = self.model_class.objects.get(
                    usuario=user,
                    livro_id=book_id
                )

            if not book:
                return None

            for key, value in book_data.items():
                setattr(book, key, value)
            book.save()
            return book
        except self.model_class.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar livro: {str(e)}")
            return None

    def delete_user_book(self, user, book_id):
        """
        Deleta um livro da estante do usuário

        Args:
            user: Usuário que está removendo o livro
            book_id: ID do livro a ser removido

        Returns:
            bool: True se o livro foi removido, False caso contrário
        """
        try:
            book = self.model_class.objects.get(
                usuario=user,
                id=book_id
            )
            book.delete()
            return True
        except self.model_class.DoesNotExist:
            return False

    def update_book_rating(self, user, book_id, rating):
        """
        Atualiza a classificação de um livro na estante do usuário.

        Args:
            user: Usuário que está classificando o livro
            book_id: ID do livro
            rating: Valor da classificação (1-5)

        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            livro = self.get_user_books_by_id(user, book_id)
            if not livro:
                return False

            livro.classificacao = rating
            livro.save(update_fields=['classificacao'])

            return True

        except Exception as e:
            logger.error(f"Erro ao atualizar classificação do livro {book_id}: {str(e)}")
            return False

