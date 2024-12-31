import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from core.domain.books.entities import BookCache, Book
from core.infrastructure.persistence.django.repositories.books.book_cache_repository import BookCacheRepository


class TestBookCacheRepository(SimpleTestCase):
    def setUp(self):
        """Configura o ambiente para cada teste"""
        self.repository = BookCacheRepository()
        self.book_mock = Mock(spec=Book)
        self.book_mock.id = '1'
        self.book_cache_mock = {
            'book_id': '1',
            'book': self.book_mock,
            'last_updated': datetime.now(),
            'data_cache': datetime.now()
        }

    def test_init(self):
        """Testa a inicialização correta do repository"""
        self.assertEqual(self.repository.model_class, BookCache)

    @patch('core.domain.books.entities.BookCache.objects')
    def test_get_book_by_id_existente(self, mock_objects):
        """Testa a obtenção de um livro do cache por ID quando existe"""
        # Arrange
        book_id = '1'
        cache_mock = Mock(spec=BookCache)
        mock_objects.get.return_value = cache_mock

        # Act
        resultado = self.repository.get_book_by_id(book_id)

        # Assert
        self.assertEqual(resultado, cache_mock)
        mock_objects.get.assert_called_once_with(book_id=book_id)

    @patch('core.domain.books.entities.BookCache.objects')
    def test_get_book_by_id_inexistente(self, mock_objects):
        """Testa a obtenção de um livro do cache por ID quando não existe"""
        # Arrange
        book_id = '999'
        mock_objects.get.side_effect = BookCache.DoesNotExist

        # Act
        resultado = self.repository.get_book_by_id(book_id)

        # Assert
        self.assertIsNone(resultado)
        mock_objects.get.assert_called_once_with(book_id=book_id)

    @patch('core.domain.books.entities.BookCache.objects')
    def test_get_or_create_cache_existente(self, mock_objects):
        """Testa obtenção de cache existente para um livro"""
        # Arrange
        cache_mock = Mock(spec=BookCache)
        mock_objects.get_or_create.return_value = (cache_mock, False)

        # Act
        resultado = self.repository.get_or_create_cache(self.book_mock)

        # Assert
        self.assertEqual(resultado, cache_mock)
        mock_objects.get_or_create.assert_called_once()
        args, kwargs = mock_objects.get_or_create.call_args
        self.assertEqual(kwargs['book'], self.book_mock)
        self.assertIn('defaults', kwargs)
        self.assertIn('last_updated', kwargs['defaults'])

    @patch('core.domain.books.entities.BookCache.objects')
    def test_get_or_create_cache_novo(self, mock_objects):
        """Testa criação de novo cache para um livro"""
        # Arrange
        cache_mock = Mock(spec=BookCache)
        mock_objects.get_or_create.return_value = (cache_mock, True)

        # Act
        resultado = self.repository.get_or_create_cache(self.book_mock)

        # Assert
        self.assertEqual(resultado, cache_mock)
        mock_objects.get_or_create.assert_called_once()
        args, kwargs = mock_objects.get_or_create.call_args
        self.assertEqual(kwargs['book'], self.book_mock)
        self.assertIn('defaults', kwargs)
        self.assertIn('last_updated', kwargs['defaults'])

    @patch('core.domain.books.entities.BookCache.objects')
    def test_clean_old_caches(self, mock_objects):
        """Testa limpeza de caches antigos"""
        # Arrange
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5
        mock_queryset.delete.return_value = None
        mock_objects.filter.return_value = mock_queryset

        # Act
        resultado = self.repository.clean_old_caches(days=30)

        # Assert
        self.assertEqual(resultado, 5)
        mock_objects.filter.assert_called_once()
        mock_queryset.count.assert_called_once()
        mock_queryset.delete.assert_called_once()

    @patch('core.domain.books.entities.BookCache.objects')
    def test_save_book(self, mock_objects):
        """Testa salvamento de livro no cache"""
        # Arrange
        book_id = '1'
        book_data = {'titulo': 'Clean Code', 'autor': 'Robert C. Martin'}
        cache_mock = Mock(spec=BookCache)
        mock_objects.salvar_book.return_value = cache_mock

        # Act
        resultado = self.repository.save_book(book_id, book_data)

        # Assert
        self.assertEqual(resultado, cache_mock)
        mock_objects.salvar_book.assert_called_once_with(book_id, book_data)

    @patch('core.domain.books.entities.BookCache.objects')
    def test_clean_old_caches_sem_caches_antigos(self, mock_objects):
        """Testa limpeza de caches quando não há caches antigos"""
        # Arrange
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        mock_queryset.delete.return_value = None
        mock_objects.filter.return_value = mock_queryset

        # Act
        resultado = self.repository.clean_old_caches(days=30)

        # Assert
        self.assertEqual(resultado, 0)
        mock_objects.filter.assert_called_once()
        mock_queryset.count.assert_called_once()
        mock_queryset.delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()