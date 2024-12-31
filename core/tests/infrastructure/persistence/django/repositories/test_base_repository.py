from django.test import SimpleTestCase  # Note a mudança de TestCase para SimpleTestCase
from django.db import models
from unittest.mock import Mock, patch
from core.infrastructure.persistence.django.repositories.base import BaseRepository


class TestBaseRepository(SimpleTestCase):
    """
    Testes para o BaseRepository usando SimpleTestCase para evitar
    interação com banco de dados
    """

    def setUp(self):
        """Configuração que roda antes de cada teste"""
        # Criamos um Mock para simular um modelo Django
        self.model_class = Mock()
        self.model_class._meta = Mock()
        self.model_class._meta.model_name = 'teste_model'
        self.repository = BaseRepository(self.model_class)

    def test_init(self):
        """Testa a inicialização do repository"""
        self.assertEqual(self.repository.model_class, self.model_class)

    def test_all(self):
        """Testa o método all() do repository"""
        # Arrange
        mock_queryset = Mock()
        self.model_class.objects.all.return_value = mock_queryset

        # Act
        result = self.repository.all()

        # Assert
        self.assertEqual(result, mock_queryset)
        self.model_class.objects.all.assert_called_once()

    def test_get_by_id_existente(self):
        """Testa busca por ID quando o objeto existe"""
        # Arrange
        mock_obj = Mock()
        self.model_class.objects.get.return_value = mock_obj

        # Act
        result = self.repository.get_by_id(1)

        # Assert
        self.assertEqual(result, mock_obj)
        self.model_class.objects.get.assert_called_once_with(id=1)

    def test_get_by_id_inexistente(self):
        """Testa busca por ID quando o objeto não existe"""
        # Arrange
        self.model_class.DoesNotExist = Exception
        self.model_class.objects.get.side_effect = self.model_class.DoesNotExist

        # Act
        result = self.repository.get_by_id(999)

        # Assert
        self.assertIsNone(result)
        self.model_class.objects.get.assert_called_once_with(id=999)

    def test_create(self):
        """Testa a criação de um novo objeto"""
        # Arrange
        mock_obj = Mock()
        self.model_class.objects.create.return_value = mock_obj
        dados = {'nome': 'Teste'}

        # Act
        result = self.repository.create(**dados)

        # Assert
        self.assertEqual(result, mock_obj)
        self.model_class.objects.create.assert_called_once_with(**dados)

    def test_update(self):
        """Testa a atualização de um objeto"""
        # Arrange
        mock_queryset = Mock()
        mock_obj = Mock()
        self.model_class.objects.filter.return_value = mock_queryset
        mock_queryset.update.return_value = 1
        mock_queryset.first.return_value = mock_obj
        dados = {'nome': 'Novo Nome'}

        # Act
        result = self.repository.update(1, **dados)

        # Assert
        self.assertEqual(result, mock_obj)
        self.model_class.objects.filter.assert_called_once_with(id=1)
        mock_queryset.update.assert_called_once_with(**dados)

    def test_delete(self):
        """Testa a deleção de um objeto"""
        # Arrange
        mock_queryset = Mock()
        self.model_class.objects.filter.return_value = mock_queryset
        mock_queryset.delete.return_value = (1, {})

        # Act
        result = self.repository.delete(1)

        # Assert
        self.assertTrue(result)
        self.model_class.objects.filter.assert_called_once_with(id=1)
        mock_queryset.delete.assert_called_once()

    def test_exists(self):
        """Testa verificação de existência"""
        # Arrange
        mock_queryset = Mock()
        self.model_class.objects.filter.return_value = mock_queryset
        mock_queryset.exists.return_value = True
        filtros = {'nome': 'Teste'}

        # Act
        result = self.repository.exists(**filtros)

        # Assert
        self.assertTrue(result)
        self.model_class.objects.filter.assert_called_once_with(**filtros)
        mock_queryset.exists.assert_called_once()

    def test_count(self):
        """Testa contagem de objetos"""
        # Arrange
        self.model_class.objects.count.return_value = 5

        # Act
        result = self.repository.count()

        # Assert
        self.assertEqual(result, 5)
        self.model_class.objects.count.assert_called_once()