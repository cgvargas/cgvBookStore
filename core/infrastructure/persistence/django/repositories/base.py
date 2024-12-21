from typing import List, Optional, TypeVar, Generic
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    model: T = None

    def __init__(self, model_class: T):
        self.model = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """Retorna uma entidade pelo ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def list_all(self) -> List[T]:
        """Retorna todas as entidades"""
        return list(self.model.objects.all())

    def create(self, **kwargs) -> T:
        """Cria uma nova entidade"""
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        """Atualiza uma entidade existente"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: T) -> bool:
        """Deleta uma entidade"""
        instance.delete()
        return True

    def filter(self, **kwargs) -> QuerySet[T]:
        """Filtra entidades baseado nos parâmetros"""
        return self.model.objects.filter(**kwargs)

    def exists(self, **kwargs) -> bool:
        """Verifica se existe entidade com os parâmetros dados"""
        return self.model.objects.filter(**kwargs).exists()