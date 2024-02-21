import json
import logging

import backoff
from aioredis import Redis

from app.services import AbstractStorage
from app.services.helpers import custom_json_encoder

logger = logging.getLogger(__name__)


class RedisStorage(AbstractStorage):
    """Класс для работы с Redis."""
    def __init__(self, redis: Redis):
        self.redis = redis

    @backoff.on_exception(backoff.expo, Exception, max_time=60)
    async def get_from_cache(self, item_id: int, model):
        """Получение записи из кеша."""
        try:
            if data := await self.redis.get(key=item_id):
                return model.parse_raw(data)
        except Exception as e:
            logger.error(f"Error fetching data from Redis: {e}")
            raise e  # Пробросить исключение для повторной попытки выполнения
        return None

    async def put_to_cache(self, validated_data, item_id: int) -> None:
        """Сохранение записи в кеш."""
        try:
            data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
            await self.redis.set(item_id, data_json)
        except Exception as e:
            logger.error(f"Error saving data to Redis: {e}")

    async def delete_from_cache(self, item_id: int) -> None:
        """Удаление записи из кеша."""
        try:
            await self.redis.delete(item_id)
        except Exception as e:
            logger.error(f"Error deleting data from Redis: {e}")
