from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractStorage(ABC):
    @abstractmethod
    async def get_from_cache(self, *args, **kwargs) -> Dict[str, List[str]]:
        pass

    @abstractmethod
    async def put_to_cache(self, *args, **kwargs) -> None:
        pass


class AsyncSearchEngine(ABC):

    @abstractmethod
    async def save(self, *args, **kwargs):
        pass

    # @abstractmethod
    # async def delete(self, *args, **kwargs):
    #     pass
    #
    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_one(self, *args, **kwargs):
        pass
