import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.attributes import flag_modified

from app.db.engine import SessionLocal, get_db
from app.db.models.categories import Categories
from app.redis import get_redis
from app.schemas.categories import Category
from app.services import AsyncSearchEngine
from app.services.helpers import CustomException
from app.services.redis_storage import RedisStorage

logger = logging.getLogger(__name__)


class CategoryService(AsyncSearchEngine):
    """Класс для работы с категориями."""
    def __init__(self, redis: Redis, db: SessionLocal):
        self.redis = redis
        self.db = db
        self.redis_storage = RedisStorage(redis=self.redis)

    async def save_top_parent(self, name: str, sql_model=Categories, pydantic_model=Category):
        """Сохранить родителя на вершине дерева."""
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
        validated_data.id = data_to_insert.id  # добавляем id, созданный sql
        await self.redis_storage.put_to_cache(validated_data=validated_data, item_id=data_to_insert.id)

    async def save_child(self, name: str, parent_id: int, sql_model=Categories, pydantic_model=Category):
        """Сохранить потомка."""
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
            validated_data.id = data_to_insert.id  # добавляем id, созданный sql
            await self.redis_storage.put_to_cache(validated_data=validated_data, item_id=data_to_insert.id)
            parent_data = pydantic_model.from_orm(selected_category)
            await self.redis_storage.put_to_cache(
                validated_data=parent_data,
                item_id=parent_data.id,
            )

    async def save(self, name: str, parent_id: Optional[int], sql_model=Categories, pydantic_model=Category):
        """Сохранить новую категорию."""
        if not parent_id:
            await self.save_top_parent(name=name, sql_model=sql_model, pydantic_model=pydantic_model)
        else:
            await self.save_child(name=name, parent_id=parent_id, sql_model=sql_model, pydantic_model=pydantic_model)

    async def update(self, item_id: int, name: str, sql_model=Categories, pydantic_model=Category):
        """Обновить категорию."""
        if category := self.get_one(item_id=item_id, sql_model=sql_model):
            category.name = name
            self.db.add(category)
            self.db.commit()  # TODO: добавить исключение
            await self.redis_storage.put_to_cache(
                validated_data=pydantic_model.from_orm(category),
                item_id=category.id,
            )

    def get_one(self, item_id: int, sql_model=Categories):
        """Получить запись из бд."""
        try:
            item = self.db.query(Categories).filter(Categories.id == item_id).first()
        except NoResultFound as error:
            logger.error(f"Не найдено результатов: {error}")
            raise CustomException(message="Не найдено результатов", code=404)
        return item

    async def get_one_from_redis(self, item_id: int, pydantic_model=Category):
        """Получить запись из редиса."""
        return await self.redis_storage.get_from_cache(item_id, model=pydantic_model)

    def get_all(self):
        """Получить все записи из бд."""
        try:
            items = self.db.query(Categories).all()
        except NoResultFound as error:
            logger.error(f"Не найдено результатов: {error}")
            raise CustomException(message="Не найдено результатов", code=404)
        return items

    async def save_categories_to_redis(self, pydantic_model=Category):
        """Сохранить все категории в редис."""
        categories = self.get_all()

        for category in categories:
            parent_data = pydantic_model.from_orm(category)
            await self.redis_storage.put_to_cache(
                validated_data=parent_data,
                item_id=parent_data.id,
            )

    async def delete(self, item_id: int, pydantic_model=Category):
        """Удалить из редиса и бд."""
        children_ids = await self.get_all_children_ids(item_id=item_id, pydantic_model=Category)
        for child_id in children_ids:
            self.db.query(Categories).filter(Categories.id == child_id).delete()
        self.db.commit()

        for child_id in children_ids:
            await self.redis_storage.delete_from_cache(child_id)

    async def get_all_children_ids(self, item_id, pydantic_model=Category):
        """Получить все id потомков."""
        async def traverse_children(node: pydantic_model):
            if children := node.children_ids:
                for child_id in children:
                    child_data = await self.redis_storage.get_from_cache(child_id, model=pydantic_model)
                    if child_data:
                        children_ids.append(child_data.id)
                        await traverse_children(child_data)

        children_ids = [item_id]
        item_data = await self.redis_storage.get_from_cache(item_id, model=pydantic_model)
        if item_data:
            await traverse_children(item_data)
        return children_ids

    async def get_all_children(self, item_id, pydantic_model=Category):
        """Получить всех потомков."""
        async def traverse_children(node: pydantic_model):
            children = []
            if node.children_ids:
                for child_id in node.children_ids:
                    child_data = await self.redis_storage.get_from_cache(child_id, model=pydantic_model)
                    if child_data:
                        children.append(child_data)
                        children.extend(await traverse_children(child_data))
            return children

        item_data = await self.redis_storage.get_from_cache(item_id, model=pydantic_model)
        if item_data:
            children = await traverse_children(item_data)
            return [item_data] + children
        return []

    async def get_categories_as_tree(self, pydantic_model=Category):
        """Получить все категории в виде дерева."""
        top_nodes = await self.get_top_tree_nodes()  # TODO: перенести в редис
        trees = []
        for top_node in top_nodes:
            tree = await self.get_all_children(top_node.id, pydantic_model)
            trees.append(tree)
        return trees

    async def get_top_tree_nodes(self, sql_model=Categories):
        """Получить вершины всех деревьев."""
        return self.db.query(sql_model).filter(sql_model.parent_id.is_(None)).all()

    async def get_all_items_from_redis(self, pydantic_model=Category):
        """Получить все записи из редиса."""
        categories = []
        keys = await self.redis.keys('*')
        for key in keys:
            data = await self.redis_storage.get_from_cache(key, pydantic_model)
            if data:
                categories.append(data)
        return categories

    async def get_category_and_parents(self, item_id: int):
        """Получить категорию и ее предков."""
        parents = []

        async def find_parents(item_id):
            category_data = await self.redis_storage.get_from_cache(item_id, Category)
            if category_data:
                parents.append(category_data)
                if category_data.parent_id:
                    await find_parents(category_data.parent_id)

        await find_parents(item_id)
        return parents


@lru_cache()
def get_base_service(
    redis: Redis = Depends(get_redis),
    db: SessionLocal = Depends(get_db),
) -> CategoryService:
    return CategoryService(redis=redis, db=db)
