import json
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
from app.services.helpers import custom_json_encoder


class BaseService(AsyncSearchEngine):
    def __init__(self, redis: Redis, db: SessionLocal):
        self.redis = redis
        self.db = db

    async def save(self, name: str, parent_id: Optional[int]):
        if not parent_id:
            validated_data = Category(
                name=name,
                level=1,
                children_ids=[],
                parent_id=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            data_to_insert = Categories(**validated_data.dict())
            self.db.add(data_to_insert)
            self.db.flush()
            self.db.commit()
            data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
            await self.redis.set(validated_data.id, data_json)
        else:
            selected_category = self.db.query(Categories).filter(Categories.id == parent_id).first()
            if selected_category:
                validated_data = Category(
                    name=name,
                    children_ids=[],
                    level=selected_category.level + 1,
                    parent_id=selected_category.id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                data_to_insert = Categories(**validated_data.dict())
                self.db.add(data_to_insert)
                self.db.flush()
                selected_category.children_ids.append(data_to_insert.id)
                flag_modified(selected_category, 'children_ids')
                self.db.add(selected_category)
                self.db.commit()
                data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
                parent_data = Category.from_orm(selected_category)
                selected_category_json = json.dumps(parent_data.dict(), default=custom_json_encoder).encode('utf-8')
                await self.redis.set(data_to_insert.id, data_json)
                await self.redis.set(selected_category.id, selected_category_json)


@lru_cache()
def get_base_service(
    redis: Redis = Depends(get_redis),
    db: SessionLocal = Depends(get_db),
) -> BaseService:
    return BaseService(redis=redis, db=db)
