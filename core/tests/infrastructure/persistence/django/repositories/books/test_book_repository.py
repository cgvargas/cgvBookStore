import unittest
from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from core.domain.books.entities import Book
from core.infrastructure.persistence.django.repositories.books.book_repository import BookRepository


class TestBookRepository(SimpleTestCase):
    def setUp(self):
        """Configura o ambiente para cada teste"""
        self.repository = BookRepository()
        self.livro_mock = {
            'id': 1,
            'titulo': 'Dom Casmurro',
            'autor': 'Machado de Assis',
            'isbn': '9788575413388',
            'ano_publicacao': 1899,
            'editora': 'Companhia das Letras',
            'destaque': True,
            'mais_vendido': True,
            'preco': 45.90,
            'descricao': 'Um dos maiores clássicos da literatura brasileira...',
        }

    def test_init(self):
        """Testa a inicialização correta do repository"""
        self.assertEqual(self.repository.model_class, Book)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_all_featured(self, mock_objects):
        """Testa a obtenção de livros em destaque"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_all_featured()

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_all_bestsellers(self, mock_objects):
        """Testa a obtenção de livros mais vendidos"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_all_bestsellers()

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(mais_vendido=True)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_featured_books_sem_parametros(self, mock_objects):
        """Testa a obtenção de livros em destaque sem parâmetros adicionais"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_featured_books()

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_featured_books_com_exclude(self, mock_objects):
        """Testa a obtenção de livros em destaque excluindo um ID específico"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.exclude.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_featured_books(exclude_id=1)

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)
        mock_objects.filter.return_value.exclude.assert_called_once_with(id=1)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_featured_books_com_order_by_string(self, mock_objects):
        """Testa a obtenção de livros em destaque com ordenação por string"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.order_by.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_featured_books(order_by='titulo')

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)
        mock_objects.filter.return_value.order_by.assert_called_once_with('titulo')

    @patch('core.domain.books.entities.Book.objects')
    def test_get_featured_books_com_order_by_lista(self, mock_objects):
        """Testa a obtenção de livros em destaque com ordenação por lista"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.order_by.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_featured_books(order_by=['-data_publicacao', 'titulo'])

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)
        mock_objects.filter.return_value.order_by.assert_called_once_with('-data_publicacao', 'titulo')

    @patch('core.domain.books.entities.Book.objects')
    def test_get_featured_books_com_limit(self, mock_objects):
        """Testa a obtenção de livros em destaque com limite"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.__getitem__.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_featured_books(limit=5)

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(destaque=True)
        mock_objects.filter.return_value.__getitem__.assert_called_once_with(slice(None, 5, None))

    @patch('core.domain.books.entities.Book.objects')
    def test_get_bestseller_books_sem_parametros(self, mock_objects):
        """Testa a obtenção de livros mais vendidos sem parâmetros"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_bestseller_books()

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(mais_vendido=True)

    @patch('core.domain.books.entities.Book.objects')
    def test_get_bestseller_books_com_order_by_string(self, mock_objects):
        """Testa a obtenção de livros mais vendidos com ordenação por string"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.order_by.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_bestseller_books(order_by='titulo')

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(mais_vendido=True)
        mock_objects.filter.return_value.order_by.assert_called_once_with('titulo')

    @patch('core.domain.books.entities.Book.objects')
    def test_get_bestseller_books_com_order_by_lista(self, mock_objects):
        """Testa a obtenção de livros mais vendidos com ordenação por lista"""
        # Arrange
        livro_mock = Mock(spec=Book)
        mock_objects.filter.return_value.order_by.return_value = [livro_mock]

        # Act
        resultado = self.repository.get_bestseller_books(order_by=['-vendas', 'titulo'])

        # Assert
        self.assertEqual(len(resultado), 1)
        mock_objects.filter.assert_called_once_with(mais_vendido=True)
        mock_objects.filter.return_value.order_by.assert_called_once_with('-vendas', 'titulo')


if __name__ == '__main__':
    unittest.main()