from abc import ABC, abstractmethod


class AsyncSearchEngine(ABC):

    @abstractmethod
    async def save(self, *args, **kwargs):
        pass

    # @abstractmethod
    # async def delete(self, *args, **kwargs):
    #     pass
    #
    # @abstractmethod
    # async def update(self, *args, **kwargs):
    #     pass
    #
    # @abstractmethod
    # async def get_all(self, *args, **kwargs):
    #     pass
    #
    # @abstractmethod
    # async def get_one(self, *args, **kwargs):
    #     pass
