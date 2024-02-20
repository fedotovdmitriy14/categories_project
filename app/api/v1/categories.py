from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Path

from app.schemas.categories import Category
from app.services.categories import CategoryService, get_base_service

router = APIRouter()


@router.post(
    '/',
)
async def post_new_category(
    parent_id: Optional[int] = Body(None),
    name: str = Body(...),
    base_service: CategoryService = Depends(get_base_service)
) -> Dict[str, str]:
    await base_service.save(name=name, parent_id=parent_id)
    return {'message': 'ok'}


@router.post(
    '/redis',
)
async def save_to_redis(
    base_service: CategoryService = Depends(get_base_service),
) -> Dict[str, str]:
    await base_service.save_categories_to_redis()
    return {'message': 'ok'}


@router.get(
    '/category-tree',
    response_model=List[List[Category]]
)
async def get_category_tree(
    base_service: CategoryService = Depends(get_base_service),
):
    return await base_service.get_categories_as_tree()


@router.get(
    '/',
)
async def get_all_categories(
    base_service: CategoryService = Depends(get_base_service),
):
    return await base_service.get_all_items_from_redis()


@router.put(
    '/{id}',
)
async def update_category(
    name: str = Body(..., embed=True),
    base_service: CategoryService = Depends(get_base_service),
    id_: int = Path(alias='id'),
) -> Dict[str, str]:
    await base_service.update(name=name, item_id=id_)
    return {'message': 'ok'}


@router.get(
    '/{id}',
    response_model=List[Category],
)
async def get_one_category(
    base_service: CategoryService = Depends(get_base_service),
    id_: int = Path(alias='id'),
):
    return await base_service.get_category_and_parents(item_id=id_)


@router.delete(
    '/{id}',
)
async def delete_category(
    base_service: CategoryService = Depends(get_base_service),
    id_: int = Path(alias='id'),
) -> Dict[str, str]:
    await base_service.delete(item_id=id_)
    return {'message': 'ok'}
