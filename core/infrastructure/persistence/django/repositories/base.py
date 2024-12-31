# core/infrastructure/persistence/django/repositories/base.py

from typing import TypeVar, Generic, Optional, Any
from django.db import models

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    """Classe base para todos os repositories"""

    def __init__(self, model_class: type[T]):
        self.model_class = model_class

    def all(self) -> models.QuerySet[T]:
        """Retorna todos os registros"""
        return self.model_class.objects.all()

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Busca um registro pelo ID
        Retorna None se não encontrar
        """
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None

    def filter(self, **kwargs) -> models.QuerySet[T]:
        """Filtra registros com base nos parâmetros fornecidos"""
        return self.model_class.objects.filter(**kwargs)

    def create(self, **kwargs) -> T:
        """Cria um novo registro"""
        return self.model_class.objects.create(**kwargs)

    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Atualiza um registro existente
        Retorna o objeto atualizado ou None se não encontrar
        """
        queryset = self.model_class.objects.filter(id=id)
        updated = queryset.update(**kwargs)
        if updated:
            return queryset.first()
        return None

    def delete(self, id: int) -> bool:
        """
        Deleta um registro
        Retorna True se deletou algo, False caso contrário
        """
        result = self.model_class.objects.filter(id=id).delete()
        return bool(result[0] > 0)

    def exists(self, **kwargs) -> bool:
        """Verifica se existe algum registro com os filtros fornecidos"""
        return self.model_class.objects.filter(**kwargs).exists()

    def count(self) -> int:
        """Retorna a contagem total de registros"""
        return self.model_class.objects.count()