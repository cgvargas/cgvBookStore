import unittest
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from core.domain.books.entities import BookShelf
from core.infrastructure.persistence.django.repositories.books.bookshelf_repository import BookShelfRepository


class TestBookShelfRepository(SimpleTestCase):
    def setUp(self):
        """Configura o ambiente para cada teste"""
        self.repository = BookShelfRepository()
        self.user_mock = Mock()
        self.user_mock.id = 1

        self.book_data_mock = {
            'titulo': 'Dom Casmurro',
            'autor': 'Machado de Assis',
            'livro_id': '123',
            'tipo': 'lido',
            'capa': 'url_da_capa.jpg',
            'data_lancamento': '1899',
            'sinopse': 'Um clássico da literatura brasileira',
            'editora': 'Companhia das Letras',
            'numero_paginas': 256,
            'isbn': '9788575413388',
            'idioma': 'pt-BR',
            'categoria': 'Literatura Brasileira',
            'manual': False
        }

    def test_init(self):
        """Testa a inicialização correta do repository"""
        self.assertEqual(self.repository.model_class, BookShelf)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_get_user_books_by_type(self, mock_objects):
        """Testa obtenção de livros do usuário por tipo"""
        # Arrange
        tipo = 'lido'
        livro_mock = Mock(spec=BookShelf)
        mock_query = Mock()
        mock_query.order_by.return_value = [livro_mock]
        mock_objects.filter.return_value = mock_query

        # Act
        resultado = self.repository.get_user_books_by_type(self.user_mock, tipo)

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(usuario=self.user_mock, tipo=tipo)
        mock_query.order_by.assert_called_once_with('-data_adicao')

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_count_valid_user_books(self, mock_objects):
        """Testa contagem de livros válidos do usuário"""
        # Arrange
        mock_query = Mock()
        mock_query.distinct.return_value.count.return_value = 5
        mock_objects.filter.return_value = mock_query

        # Act
        resultado = self.repository.count_valid_user_books(self.user_mock)

        # Assert
        self.assertEqual(resultado, 5)
        mock_objects.filter.assert_called_once_with(
            usuario=self.user_mock,
            titulo__isnull=False
        )
        mock_query.distinct.assert_called_once()

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_book_exists_in_shelf_true(self, mock_objects):
        """Testa verificação de existência de livro na estante quando existe"""
        # Arrange
        book_id = '123'
        mock_objects.filter.return_value.exists.return_value = True

        # Act
        resultado = self.repository.book_exists_in_shelf(self.user_mock, book_id)

        # Assert
        self.assertTrue(resultado)
        mock_objects.filter.assert_called_once_with(usuario=self.user_mock, livro_id=book_id)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_book_exists_in_shelf_false(self, mock_objects):
        """Testa verificação de existência de livro na estante quando não existe"""
        # Arrange
        book_id = '123'
        mock_objects.filter.return_value.exists.return_value = False

        # Act
        resultado = self.repository.book_exists_in_shelf(self.user_mock, book_id)

        # Assert
        self.assertFalse(resultado)
        mock_objects.filter.assert_called_once_with(usuario=self.user_mock, livro_id=book_id)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_add_google_book_to_shelf(self, mock_objects):
        """Testa adição de livro do Google Books à estante"""
        # Arrange
        google_book_id = '123'
        book_type = 'lido'
        livro_mock = Mock(spec=BookShelf)
        mock_objects.create.return_value = livro_mock

        # Act
        resultado = self.repository.add_google_book_to_shelf(
            self.user_mock,
            google_book_id,
            book_type,
            self.book_data_mock
        )

        # Assert
        self.assertEqual(resultado, livro_mock)
        mock_objects.create.assert_called_once()
        args, kwargs = mock_objects.create.call_args
        self.assertEqual(kwargs['usuario'], self.user_mock)
        self.assertEqual(kwargs['livro_id'], google_book_id)
        self.assertEqual(kwargs['tipo'], book_type)
        self.assertEqual(kwargs['titulo'], self.book_data_mock['titulo'])
        self.assertFalse(kwargs['manual'])

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_transfer_book_success(self, mock_objects):
        """Testa transferência bem-sucedida de livro para outra prateleira"""
        # Arrange
        book_id = 1
        new_type = 'lendo'
        livro_mock = Mock(spec=BookShelf)
        livro_mock.save = Mock()
        mock_objects.get.return_value = livro_mock

        # Mock para TIPO_CHOICES
        self.repository.model_class.TIPO_CHOICES = [('lendo', 'Lendo'), ('lido', 'Lido')]

        # Act
        resultado = self.repository.transfer_book(self.user_mock, book_id, new_type)

        # Assert
        self.assertEqual(resultado, livro_mock)
        mock_objects.get.assert_called_once_with(id=book_id, usuario=self.user_mock)
        self.assertEqual(livro_mock.tipo, new_type)
        livro_mock.save.assert_called_once()

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_transfer_book_invalid_type(self, mock_objects):
        """Testa transferência de livro com tipo inválido"""
        # Arrange
        book_id = 1
        new_type = 'tipo_invalido'
        livro_mock = Mock(spec=BookShelf)
        mock_objects.get.return_value = livro_mock

        # Mock para TIPO_CHOICES
        self.repository.model_class.TIPO_CHOICES = [('lendo', 'Lendo'), ('lido', 'Lido')]

        # Act
        resultado = self.repository.transfer_book(self.user_mock, book_id, new_type)

        # Assert
        self.assertIsNone(resultado)
        mock_objects.get.assert_called_once_with(id=book_id, usuario=self.user_mock)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_transfer_book_not_found(self, mock_objects):
        """Testa transferência de livro inexistente"""
        # Arrange
        book_id = 999
        new_type = 'lendo'
        mock_objects.get.side_effect = self.repository.model_class.DoesNotExist

        # Act
        resultado = self.repository.transfer_book(self.user_mock, book_id, new_type)

        # Assert
        self.assertIsNone(resultado)
        mock_objects.get.assert_called_once_with(id=book_id, usuario=self.user_mock)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_add_book_to_shelf(self, mock_objects):
        """Testa adição de livro à estante"""
        # Arrange
        livro_mock = Mock(spec=BookShelf)
        mock_objects.create.return_value = livro_mock

        # Act
        resultado = self.repository.add_book_to_shelf(self.user_mock, self.book_data_mock)

        # Assert
        self.assertEqual(resultado, livro_mock)
        mock_objects.create.assert_called_once_with(
            usuario=self.user_mock,
            **self.book_data_mock
        )

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_get_user_book_by_id_existente(self, mock_objects):
        """Testa obtenção de livro específico da estante quando existe"""
        # Arrange
        book_id = 1
        livro_mock = Mock(spec=BookShelf)
        mock_objects.get.return_value = livro_mock

        # Act
        resultado = self.repository.get_user_book_by_id(self.user_mock, book_id)

        # Assert
        self.assertEqual(resultado, livro_mock)
        mock_objects.get.assert_called_once_with(id=book_id, usuario=self.user_mock)

    @patch('core.domain.books.entities.BookShelf.objects')
    def test_get_user_book_by_id_inexistente(self, mock_objects):
        """Testa obtenção de livro específico da estante quando não existe"""
        # Arrange
        book_id = 999
        mock_objects.get.side_effect = self.repository.model_class.DoesNotExist

        # Act
        resultado = self.repository.get_user_book_by_id(self.user_mock, book_id)

        # Assert
        self.assertIsNone(resultado)
        mock_objects.get.assert_called_once_with(id=book_id, usuario=self.user_mock)


if __name__ == '__main__':
    unittest.main()