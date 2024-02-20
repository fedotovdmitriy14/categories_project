import json
from datetime import datetime
from typing import Optional

from aioredis import Redis
from sqlalchemy.orm.attributes import flag_modified

from app.db.engine import SessionLocal
from app.db.models.categories import Categories
from app.schemas.categories import Category


def custom_json_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


async def save_to_db(db: SessionLocal, redis: Redis, name: str, parent_id: Optional[int]):
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
        db.add(data_to_insert)
        db.flush()
        db.commit()
        data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
        await redis.set(validated_data.id, data_json)
    else:
        selected_category = db.query(Categories).filter(Categories.id == parent_id).first()
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
            db.add(data_to_insert)
            db.flush()
            selected_category.children_ids.append(data_to_insert.id)
            flag_modified(selected_category, 'children_ids')
            db.add(selected_category)
            db.commit()
            data_json = json.dumps(validated_data.dict(), default=custom_json_encoder).encode('utf-8')
            parent_data = Category.from_orm(selected_category)
            selected_category_json = json.dumps(parent_data.dict(), default=custom_json_encoder).encode('utf-8')
            await redis.set(data_to_insert.id, data_json)
            await redis.set(selected_category.id, selected_category_json)
