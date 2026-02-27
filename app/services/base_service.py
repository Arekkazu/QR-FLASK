from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseService(ABC):
    @abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """Crear un nuevo recurso"""
        pass

    @abstractmethod
    def get(self, *args, **kwargs) -> Optional[Any]:
        """Obtener un recurso específico"""
        pass

    @abstractmethod
    def update(self, *args, **kwargs) -> Any:
        """Actualizar un recurso existente"""
        pass

    @abstractmethod
    def delete(self, *args, **kwargs) -> None:
        """Eliminar un recurso"""
        pass
