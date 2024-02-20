from datetime import datetime
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.orm.attributes import flag_modified

from app.db.engine import SessionLocal, get_db
from app.db.models.categories import Categories
from app.redis import get_redis
from app.schemas.categories import Category
from app.services import AsyncSearchEngine
from app.services.redis_storage import RedisStorage


class BaseService(AsyncSearchEngine):
    def __init__(self, redis: Redis, db: SessionLocal):
        self.redis = redis
        self.db = db
        self.redis_storage = RedisStorage(redis=self.redis)

    # def _validate_data(self, model: Categories, pydantic_schema: Category, data: Dict[str, str]) -> Category:
    #     """Валидирует данные в pydantic и переводит в модель sqlalchemy."""
    #     validated_schema = pydantic_schema(**data)
    #     return model(**validated_schema.dict())

    async def save_top_parent(self, name: str, sql_model=Categories, pydantic_model=Category):
        validated_data = pydantic_model(
            name=name,
            level=1,
            children_ids=[],
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        data_to_insert = sql_model(**validated_data.dict())
        self.db.add(data_to_insert)
        self.db.flush()
        self.db.commit()
        await self.redis_storage.put_to_cache(validated_data=validated_data, item_id=data_to_insert.id)

    async def save_child(self, name: str, parent_id: int, sql_model=Categories, pydantic_model=Category):
        selected_category = self.db.query(Categories).filter(Categories.id == parent_id).first()
        if selected_category:
            validated_data = pydantic_model(
                name=name,
                children_ids=[],
                level=selected_category.level + 1,
                parent_id=selected_category.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            data_to_insert = sql_model(**validated_data.dict())
            self.db.add(data_to_insert)
            self.db.flush()  # получить айди без коммита транзакции
            selected_category.children_ids.append(data_to_insert.id)
            flag_modified(selected_category, 'children_ids')  # иначе алхимия не увидит изменения в массиве
            self.db.add(selected_category)
            self.db.commit()
            await self.redis_storage.put_to_cache(validated_data=validated_data, item_id=data_to_insert.id)
            parent_data = pydantic_model.from_orm(selected_category)
            await self.redis_storage.put_to_cache(
                validated_data=parent_data,
                item_id=parent_data.id,
            )

    async def save(self, name: str, parent_id: Optional[int], sql_model=Categories, pydantic_model=Category):
        if not parent_id:
            await self.save_top_parent(name=name, sql_model=sql_model, pydantic_model=pydantic_model)
        else:
            await self.save_child(name=name, parent_id=parent_id, sql_model=sql_model, pydantic_model=pydantic_model)

    async def update(self, item_id: int, name: str, sql_model=Categories, pydantic_model=Category):
        if category := self.get_one(item_id=item_id, sql_model=sql_model):
            category.name = name
            self.db.add(category)
            self.db.commit()  # TODO: добавить исключение
            await self.redis_storage.put_to_cache(
                validated_data=pydantic_model.from_orm(category),
                item_id=category.id,
            )

    def get_one(self, item_id: int, sql_model=Categories):
        return self.db.query(Categories).filter(Categories.id == item_id).first()

    async def get_one_from_redis(self, item_id: int, pydantic_model=Category):
        item = await self.redis_storage.get_from_cache(item_id, model=pydantic_model)
        print(f'{item=}')
        return item

    def get_all(self):
        return self.db.query(Categories).all()

    async def save_categories_to_redis(self, pydantic_model=Category):
        categories = self.get_all()

        for category in categories:
            parent_data = pydantic_model.from_orm(category)
            await self.redis_storage.put_to_cache(
                validated_data=parent_data,
                item_id=parent_data.id,
            )


@lru_cache()
def get_base_service(
    redis: Redis = Depends(get_redis),
    db: SessionLocal = Depends(get_db),
) -> BaseService:
    return BaseService(redis=redis, db=db)
