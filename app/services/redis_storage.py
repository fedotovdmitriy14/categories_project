import json

from aioredis import Redis

from app.services import AbstractStorage
from app.services.helpers import custom_json_encoder


class RedisStorage(AbstractStorage):
    """Класс для работы с редисом."""
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_from_cache(self, item_id: int, model):
        """пробуем получить запись по id из кеша"""
        if data := await self.redis.get(key=item_id):
            return model.parse_raw(data)
        return None

    async def put_to_cache(self, validated_data, item_id: int) -> None:
        """кладем запись в кеш"""
        data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
        await self.redis.set(item_id, data_json)
